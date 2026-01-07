# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

SEO MCP is a Model Context Protocol (MCP) server that provides SEO tools by interfacing with Ahrefs' free tools. It uses CapSolver to handle Cloudflare Turnstile CAPTCHA challenges and caches authentication signatures for improved performance.

## Development Commands

```bash
# Install dependencies
uv sync

# Run the MCP server locally
python main.py
# or
seo-mcp

# Install in editable mode for development
uv pip install -e .
```

## Environment Variables

- `CAPSOLVER_API_KEY` - Required for production. Get from https://dashboard.capsolver.com
- `DEBUG` - Set to any truthy value to enable file logging to `logs/` directory

## Architecture

The project is built on FastMCP and exposes four MCP tools:

```
src/seo_mcp/
├── server.py      # FastMCP server, tool definitions, CAPTCHA solving via CapSolver
├── backlinks.py   # Backlink analysis with signature caching (signature_cache.json)
├── keywords.py    # Keyword ideas and difficulty scoring
├── traffic.py     # Traffic estimation and analysis
└── logger.py      # Optional debug logging (activated by DEBUG env var)
```

### Request Flow

1. MCP tool receives request
2. `get_capsolver_token()` in server.py solves Cloudflare Turnstile CAPTCHA
3. Token is used to authenticate with Ahrefs API
4. For backlinks: signatures are cached locally to avoid repeated CAPTCHA solves
5. Results are formatted and returned

### Key Patterns

- All Ahrefs API calls go through the v4 API endpoints (e.g., `ahrefs.com/v4/stGetFreeBacklinksOverview`)
- Signature caching in `backlinks.py` stores domain-specific auth data with expiration checking
- Each tool module has its own formatting functions to simplify raw API responses

## MCP Tools

| Tool | Purpose |
|------|---------|
| `get_backlinks_list(domain)` | Domain backlink analysis with DR, anchors, link attributes |
| `keyword_generator(keyword, country, search_engine)` | Keyword ideas including question-based keywords |
| `get_traffic(domain_or_url, country, mode)` | Traffic estimation, top pages, country distribution |
| `keyword_difficulty(keyword, country)` | KD score with SERP analysis |
