# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Important Notice

**This MCP is for educational and research purposes only.** Users must comply with all third-party terms of service. See LICENSE for details.

## What This MCP Does

SEO Research MCP provides four SEO research tools powered by Ahrefs data:

| Tool | What to Ask | Example |
|------|-------------|---------|
| `get_backlinks_list` | Backlink analysis for any domain | "Show me backlinks for competitor.com" |
| `keyword_generator` | Keyword ideas from seed keywords | "Find keywords related to 'react hooks'" |
| `get_traffic` | Traffic estimates for websites | "What's the traffic for github.com?" |
| `keyword_difficulty` | How hard a keyword is to rank for | "Check difficulty for 'best laptop 2025'" |

## How to Use These Tools

Once configured, simply ask naturally:

```
"Analyze backlinks for example.com"
"Generate keyword ideas for 'python tutorial'"
"Show traffic data for shopify.com"
"What's the keyword difficulty for 'ai tools'?"
```

### Tool Parameters

**get_backlinks_list(domain)**
- `domain`: The website to analyze (e.g., "example.com")

**keyword_generator(keyword, country?, search_engine?)**
- `keyword`: Seed keyword to expand
- `country`: Country code like "us", "uk", "de" (default: "us")
- `search_engine`: "Google", "Bing", etc. (default: "Google")

**get_traffic(domain_or_url, country?, mode?)**
- `domain_or_url`: Website or specific URL
- `country`: Filter by country (default: all countries)
- `mode`: "subdomains" (include all) or "exact" (just this URL)

**keyword_difficulty(keyword, country?)**
- `keyword`: Keyword to check
- `country`: Target country (default: "us")

## Setup Requirements

1. **CapSolver API Key** - Required for CAPTCHA solving
   - Get one at: https://dashboard.capsolver.com
   - Set as environment variable: `CAPSOLVER_API_KEY`

2. **Python 3.10+** - Required runtime

## Development Commands

```bash
# Install dependencies
uv sync

# Run locally
python main.py
# or
seo-mcp

# Install in editable mode
uv pip install -e .
```

## Project Structure

```
src/seo_mcp/
├── server.py      # MCP server & CAPTCHA handling
├── backlinks.py   # Backlink analysis (with caching)
├── keywords.py    # Keyword research & difficulty
├── traffic.py     # Traffic estimation
└── logger.py      # Debug logging (set DEBUG=1)
```

## Troubleshooting

- **No results?** Domain may not be indexed by Ahrefs
- **Rate limited?** Wait a few minutes between requests
- **API key error?** Check CAPSOLVER_API_KEY is set correctly
