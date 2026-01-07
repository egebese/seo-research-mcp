"""
SEO MCP Server: A free SEO tool MCP (Model Control Protocol) service based on Ahrefs data. Includes features such as backlinks, keyword ideas, and more.
"""
import requests
import time
import os
import urllib.parse
from typing import Dict, List, Optional, Any, Literal

from fastmcp import FastMCP

from seo_mcp.backlinks import get_backlinks, load_signature_from_cache, get_signature_and_overview
from seo_mcp.keywords import get_keyword_ideas, get_keyword_difficulty
from seo_mcp.traffic import check_traffic


mcp = FastMCP("SEO MCP")

# CAPTCHA Provider API Keys
# Priority: CapSolver > Anti-Captcha
# At least one must be configured for the service to work
capsolver_api_key = os.environ.get("CAPSOLVER_API_KEY")
anticaptcha_api_key = os.environ.get("ANTICAPTCHA_API_KEY")


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
    res = requests.post("https://api.capsolver.com/createTask", json=payload)
    resp = res.json()
    task_id = resp.get("taskId")
    if not task_id:
        return None

    while True:
        time.sleep(1)
        payload = {"clientKey": capsolver_api_key, "taskId": task_id}
        res = requests.post("https://api.capsolver.com/getTaskResult", json=payload)
        resp = res.json()
        status = resp.get("status")
        if status == "ready":
            token = resp.get("solution", {}).get('token')
            return token
        if status == "failed" or resp.get("errorId"):
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
    res = requests.post("https://api.anti-captcha.com/createTask", json=payload)
    resp = res.json()

    if resp.get("errorId", 0) != 0:
        return None

    task_id = resp.get("taskId")
    if not task_id:
        return None

    while True:
        time.sleep(1)
        payload = {"clientKey": anticaptcha_api_key, "taskId": task_id}
        res = requests.post("https://api.anti-captcha.com/getTaskResult", json=payload)
        resp = res.json()

        if resp.get("errorId", 0) != 0:
            return None

        status = resp.get("status")
        if status == "ready":
            token = resp.get("solution", {}).get("token")
            return token
        if status == "failed":
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
        token = get_captcha_token(site_url)
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


def main():
    """Run the MCP server"""
    mcp.run()


if __name__ == "__main__":
    main()
