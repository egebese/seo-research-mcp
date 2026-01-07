"""
SEO MCP Server: A free SEO tool MCP (Model Control Protocol) service based on Ahrefs data. Includes features such as backlinks, keyword ideas, and more.
"""
import json
import requests
import time
import os
import urllib.parse
from typing import Dict, List, Optional, Any, Literal

from fastmcp import FastMCP
from openai import OpenAI

from seo_mcp.backlinks import get_backlinks, load_signature_from_cache, get_signature_and_overview
from seo_mcp.keywords import get_keyword_ideas, get_keyword_difficulty
from seo_mcp.traffic import check_traffic


mcp = FastMCP("SEO MCP")

# CAPTCHA Provider API Keys
# Priority: CapSolver > Anti-Captcha
# At least one must be configured for the service to work
capsolver_api_key = os.environ.get("CAPSOLVER_API_KEY")
anticaptcha_api_key = os.environ.get("ANTICAPTCHA_API_KEY")

# OpenRouter API Key (for AI search queries feature)
# OpenRouter provides access to multiple AI models via a unified API
openrouter_api_key = os.environ.get("OPENROUTER_API_KEY")

# Request timeout in seconds
REQUEST_TIMEOUT = 30

# Maximum polling attempts for CAPTCHA solving (prevents infinite loops)
MAX_POLLING_ATTEMPTS = 120  # 120 attempts * 1 second = 2 minutes max

# OpenAI prompt for generating search queries
SEARCH_QUERY_PROMPT = """You are an expert SEO researcher. Given the keyword "{keyword}", generate exactly {count} Google search queries that would help thoroughly research this topic.

For each query, categorize the search intent as one of:
- informational: seeking knowledge (what, how, why, guide, tutorial)
- commercial: researching before purchase (best, top, reviews, comparison, vs)
- transactional: ready to take action (buy, price, discount, near me, order)
- navigational: looking for specific site/brand

Return a JSON object with a "queries" array containing objects with "query" and "intent" fields.
Language: {language}

Example output:
{{"queries": [
  {{"query": "what is coworking space", "intent": "informational"}},
  {{"query": "best coworking spaces in city", "intent": "commercial"}}
]}}

Generate diverse queries covering different angles and intents."""


def get_capsolver_token(site_url: str) -> Optional[str]:
    """
    Use CapSolver to solve the captcha and get a token

    Args:
        site_url: Site URL to query

    Returns:
        Verification token or None if failed
    """
    if not capsolver_api_key:
        return None

    payload = {
        "clientKey": capsolver_api_key,
        "task": {
            "type": 'AntiTurnstileTaskProxyLess',
            "websiteKey": "0x4AAAAAAAAzi9ITzSN9xKMi",
            "websiteURL": site_url,
            "metadata": {
                "action": ""
            }
        }
    }
    res = requests.post("https://api.capsolver.com/createTask", json=payload, timeout=REQUEST_TIMEOUT)
    resp = res.json()
    task_id = resp.get("taskId")
    if not task_id:
        return None

    for _ in range(MAX_POLLING_ATTEMPTS):
        time.sleep(1)
        payload = {"clientKey": capsolver_api_key, "taskId": task_id}
        res = requests.post("https://api.capsolver.com/getTaskResult", json=payload, timeout=REQUEST_TIMEOUT)
        resp = res.json()
        status = resp.get("status")
        if status == "ready":
            token = resp.get("solution", {}).get('token')
            return token
        if status == "failed" or resp.get("errorId"):
            return None

    # Max attempts reached
    return None


def get_anticaptcha_token(site_url: str) -> Optional[str]:
    """
    Use Anti-Captcha to solve the captcha and get a token

    Args:
        site_url: Site URL to query

    Returns:
        Verification token or None if failed
    """
    if not anticaptcha_api_key:
        return None

    payload = {
        "clientKey": anticaptcha_api_key,
        "task": {
            "type": "TurnstileTaskProxyless",
            "websiteURL": site_url,
            "websiteKey": "0x4AAAAAAAAzi9ITzSN9xKMi"
        }
    }
    res = requests.post("https://api.anti-captcha.com/createTask", json=payload, timeout=REQUEST_TIMEOUT)
    resp = res.json()

    if resp.get("errorId", 0) != 0:
        return None

    task_id = resp.get("taskId")
    if not task_id:
        return None

    for _ in range(MAX_POLLING_ATTEMPTS):
        time.sleep(1)
        payload = {"clientKey": anticaptcha_api_key, "taskId": task_id}
        res = requests.post("https://api.anti-captcha.com/getTaskResult", json=payload, timeout=REQUEST_TIMEOUT)
        resp = res.json()

        if resp.get("errorId", 0) != 0:
            return None

        status = resp.get("status")
        if status == "ready":
            token = resp.get("solution", {}).get("token")
            return token
        if status == "failed":
            return None

    # Max attempts reached
    return None


def get_captcha_token(site_url: str) -> str:
    """
    Get CAPTCHA token using available provider.
    Priority: CapSolver > Anti-Captcha

    Args:
        site_url: Site URL to query

    Returns:
        Verification token

    Raises:
        Exception: If no provider is configured or solving fails
    """
    if not capsolver_api_key and not anticaptcha_api_key:
        raise Exception(
            "No CAPTCHA provider configured. "
            "Set CAPSOLVER_API_KEY or ANTICAPTCHA_API_KEY environment variable."
        )

    # Try CapSolver first (priority)
    if capsolver_api_key:
        token = get_capsolver_token(site_url)
        if token:
            return token

    # Fallback to Anti-Captcha
    if anticaptcha_api_key:
        token = get_anticaptcha_token(site_url)
        if token:
            return token

    raise Exception("Failed to solve CAPTCHA with available provider(s)")


@mcp.tool()
def get_backlinks_list(domain: str) -> Optional[Dict[str, Any]]:
    """
    Get backlinks list for the specified domain
    Args:
        domain (str): The domain to query
    Returns:
        List of backlinks for the domain, containing title, URL, domain rating, etc.
    """
    # Try to get signature from cache
    signature, valid_until, overview_data = load_signature_from_cache(domain)
    
    # If no valid signature in cache, get a new one
    if not signature or not valid_until:
        # Step 1: Get token
        site_url = f"https://ahrefs.com/backlink-checker/?input={domain}&mode=subdomains"
        token = get_captcha_token(site_url)

        # Step 2: Get signature and validUntil
        signature, valid_until, overview_data = get_signature_and_overview(token, domain)
        if not signature or not valid_until:
            raise Exception(f"Failed to get signature for domain: {domain}")
    
    # Step 3: Get backlinks list
    backlinks = get_backlinks(signature, valid_until, domain)
    return {
        "overview": overview_data,
        "backlinks": backlinks
    }


@mcp.tool()
def keyword_generator(keyword: str, country: str = "us", search_engine: str = "Google") -> Optional[List[str]]:
    """
    Get keyword ideas for the specified keyword
    """
    site_url = f"https://ahrefs.com/keyword-generator/?country={country}&input={urllib.parse.quote(keyword)}"
    token = get_captcha_token(site_url)
    return get_keyword_ideas(token, keyword, country, search_engine)


@mcp.tool()
def get_traffic(domain_or_url: str, country: str = "None", mode: Literal["subdomains", "exact"] = "subdomains") -> Optional[Dict[str, Any]]:
    """
    Check the estimated search traffic for any website. 

    Args:
        domain_or_url (str): The domain or URL to query
        country (str): The country to query, default is "None"
        mode (["subdomains", "exact"]): The mode to use for the query
    Returns:
        Traffic data for the specified domain or URL
    """
    site_url = f"https://ahrefs.com/traffic-checker/?input={domain_or_url}&mode={mode}"
    token = get_captcha_token(site_url)
    return check_traffic(token, domain_or_url, mode, country)


@mcp.tool()
def keyword_difficulty(keyword: str, country: str = "us") -> Optional[Dict[str, Any]]:
    """
    Get keyword difficulty for the specified keyword
    """
    site_url = f"https://ahrefs.com/keyword-difficulty/?country={country}&input={urllib.parse.quote(keyword)}"
    token = get_captcha_token(site_url)
    return get_keyword_difficulty(token, keyword, country)


@mcp.tool()
def ai_search_queries(
    keyword: str,
    count: int = 10,
    model: str = "openai/gpt-4o-mini",
    language: str = "en"
) -> Optional[Dict[str, Any]]:
    """
    Generate AI-powered search queries for keyword research.

    Uses OpenRouter to generate search queries that an AI would use
    to research a topic, categorized by search intent.

    Args:
        keyword: The keyword/topic to research
        count: Number of queries to generate (default: 10)
        model: Model to use via OpenRouter (default: openai/gpt-4o-mini)
               Examples: openai/gpt-4o-mini, openai/gpt-4o, anthropic/claude-3-haiku
        language: Language for queries (default: en)

    Returns:
        Dictionary with categorized search queries
    """
    if not openrouter_api_key:
        raise Exception(
            "OpenRouter API key not configured. "
            "Set OPENROUTER_API_KEY environment variable."
        )

    client = OpenAI(
        api_key=openrouter_api_key,
        base_url="https://openrouter.ai/api/v1"
    )

    prompt = SEARCH_QUERY_PROMPT.format(
        keyword=keyword,
        count=count,
        language=language
    )

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are an SEO expert. Return only valid JSON."},
            {"role": "user", "content": prompt}
        ],
        timeout=REQUEST_TIMEOUT
    )

    # Safely parse JSON response
    content = response.choices[0].message.content if response.choices else None
    queries = []
    error = None

    if content:
        try:
            result = json.loads(content)
            queries = result.get("queries", [])
        except json.JSONDecodeError as e:
            error = f"JSON parsing error: {str(e)}"
        except Exception as e:
            error = f"Unexpected error parsing response: {str(e)}"
    else:
        error = "Empty response from model"

    response_data = {
        "keyword": keyword,
        "queries": queries,
        "model_used": model,
        "total_queries": len(queries)
    }

    if error:
        response_data["error"] = error

    return response_data


def main():
    """Run the MCP server"""
    mcp.run()


if __name__ == "__main__":
    main()
