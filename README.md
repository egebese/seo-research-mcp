# SEO Research MCP

A free SEO research tool using [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) powered by Ahrefs data. Get backlink analysis, keyword research, traffic estimation, and more — directly in your AI-powered IDE.

> **Disclaimer:** This MCP service is for educational purposes only. Please use responsibly.

## Features

| Feature | Description |
|---------|-------------|
| **Backlink Analysis** | Domain rating, anchor text, link attributes, edu/gov filters |
| **Keyword Research** | Generate keyword ideas from seed keywords with difficulty scores |
| **Traffic Analysis** | Estimate website traffic, top pages, country distribution |
| **Keyword Difficulty** | KD score with full SERP analysis |

## Prerequisites

- Python 3.10+
- [CapSolver](https://dashboard.capsolver.com/passport/register?inviteCode=VK9BLtwYlZxi) API key (for CAPTCHA solving)

## Installation

### From PyPI

```bash
pip install seo-mcp
# or
uv pip install seo-mcp
```

### From Source

```bash
git clone https://github.com/egebese/seo-research-mcp.git
cd seo-research-mcp
pip install -e .
```

## IDE Setup Guides

<details>
<summary><strong>Claude Desktop</strong></summary>

### Option 1: Manual Configuration

1. Open Claude Desktop → Settings → Developer → Edit Config
2. Add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "seo-research": {
      "command": "uvx",
      "args": ["--python", "3.10", "seo-mcp"],
      "env": {
        "CAPSOLVER_API_KEY": "CAP-xxxxxx"
      }
    }
  }
}
```

3. Restart Claude Desktop
4. Look for the hammer/tools icon in the bottom-right corner

**Config file locations:**
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`

</details>

<details>
<summary><strong>Claude Code</strong></summary>

### Option 1: CLI Command

```bash
claude mcp add seo-research --scope user -- uvx --python 3.10 seo-mcp
```

Then set the environment variable:
```bash
export CAPSOLVER_API_KEY="CAP-xxxxxx"
```

### Option 2: Configuration File

Add to `~/.claude.json`:

```json
{
  "mcpServers": {
    "seo-research": {
      "command": "uvx",
      "args": ["--python", "3.10", "seo-mcp"],
      "env": {
        "CAPSOLVER_API_KEY": "CAP-xxxxxx"
      }
    }
  }
}
```

### Verify Installation

```bash
claude mcp list
```

</details>

<details>
<summary><strong>Cursor</strong></summary>

### Option 1: Global Configuration

Create or edit `~/.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "seo-research": {
      "command": "uvx",
      "args": ["--python", "3.10", "seo-mcp"],
      "env": {
        "CAPSOLVER_API_KEY": "CAP-xxxxxx"
      }
    }
  }
}
```

### Option 2: Project Configuration

Create `.cursor/mcp.json` in your project root with the same content.

### Verify Installation

1. Go to **File → Preferences → Cursor Settings**
2. Select **MCP** in the sidebar
3. Check that "seo-research" appears under Available Tools

</details>

<details>
<summary><strong>Windsurf</strong></summary>

### Configuration

1. Open Windsurf Settings: `Cmd+Shift+P` (Mac) / `Ctrl+Shift+P` (Windows/Linux)
2. Type "Open Windsurf Settings"
3. Navigate to **Cascade → MCP Servers**
4. Click "Edit raw mcp_config.json" and add:

```json
{
  "mcpServers": {
    "seo-research": {
      "command": "uvx",
      "args": ["--python", "3.10", "seo-mcp"],
      "env": {
        "CAPSOLVER_API_KEY": "CAP-xxxxxx"
      }
    }
  }
}
```

**Config file location:** `~/.codeium/windsurf/mcp_config.json`

</details>

<details>
<summary><strong>VS Code (GitHub Copilot)</strong></summary>

> Requires VS Code 1.102+ with GitHub Copilot

### Configuration

Create `.vscode/mcp.json` in your workspace:

```json
{
  "servers": {
    "seo-research": {
      "command": "uvx",
      "args": ["--python", "3.10", "seo-mcp"],
      "env": {
        "CAPSOLVER_API_KEY": "CAP-xxxxxx"
      }
    }
  }
}
```

### Enable the Server

1. Open the file and click the **Start** button that appears
2. In Chat view, click the **Tools** button to toggle MCP tools on/off
3. Use `#tool_name` in prompts to invoke specific tools

</details>

<details>
<summary><strong>Zed</strong></summary>

### Configuration

Add to your Zed `settings.json`:

```json
{
  "context_servers": {
    "seo-research": {
      "command": {
        "path": "uvx",
        "args": ["--python", "3.10", "seo-mcp"],
        "env": {
          "CAPSOLVER_API_KEY": "CAP-xxxxxx"
        }
      }
    }
  }
}
```

### Verify Installation

1. Open the Agent Panel settings
2. Check the indicator dot next to "seo-research"
3. Green dot = Server is active

</details>

## API Reference

### `get_backlinks_list(domain)`

Get backlinks for a domain.

```python
# Parameters
domain: str  # e.g., "example.com"

# Returns
{
  "overview": {
    "domainRating": 76,
    "backlinks": 1500,
    "refDomains": 300
  },
  "backlinks": [
    {
      "anchor": "Example link",
      "domainRating": 76,
      "title": "Page title",
      "urlFrom": "https://source.com/page",
      "urlTo": "https://example.com/page",
      "edu": false,
      "gov": false
    }
  ]
}
```

### `keyword_generator(keyword, country?, search_engine?)`

Generate keyword ideas from a seed keyword.

```python
# Parameters
keyword: str        # Seed keyword
country: str        # Country code (default: "us")
search_engine: str  # Search engine (default: "Google")

# Returns
[
  {
    "keyword": "example keyword",
    "volume": 1000,
    "difficulty": 45,
    "cpc": 2.5
  }
]
```

### `get_traffic(domain_or_url, country?, mode?)`

Estimate search traffic for a website.

```python
# Parameters
domain_or_url: str  # Domain or full URL
country: str        # Country filter (default: "None")
mode: str           # "subdomains" | "exact" (default: "subdomains")

# Returns
{
  "traffic_history": [...],
  "traffic": {
    "trafficMonthlyAvg": 50000,
    "costMontlyAvg": 25000
  },
  "top_pages": [...],
  "top_countries": [...],
  "top_keywords": [...]
}
```

### `keyword_difficulty(keyword, country?)`

Get keyword difficulty score with SERP analysis.

```python
# Parameters
keyword: str   # Keyword to analyze
country: str   # Country code (default: "us")

# Returns
{
  "difficulty": 45,
  "serp": [...],
  "related": [...]
}
```

## How It Works

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   MCP       │────▶│  CapSolver  │────▶│   Ahrefs    │────▶│  Formatted  │
│   Request   │     │  (CAPTCHA)  │     │    API      │     │   Response  │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
```

1. Your AI IDE sends an MCP request
2. CapSolver solves the Cloudflare Turnstile CAPTCHA
3. Authentication token is used to query Ahrefs API
4. Results are cached and formatted for your AI assistant

## Development

```bash
git clone https://github.com/egebese/seo-research-mcp.git
cd seo-research-mcp
uv sync
python main.py
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| CapSolver API key error | Verify `CAPSOLVER_API_KEY` environment variable is set |
| Rate limiting | Reduce request frequency |
| No results returned | Domain may not be indexed by Ahrefs |
| Server not appearing | Restart your IDE after config changes |

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=egebese/seo-research-mcp&type=Date)](https://star-history.com/#egebese/seo-research-mcp&Date)

## License

MIT License - See [LICENSE](LICENSE) file

## Credits

This project is a fork of [seo-mcp](https://github.com/cnych/seo-mcp) by [@cnych](https://github.com/cnych). Special thanks to the original author for creating this tool.
