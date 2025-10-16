# Quick Start Guide

Get up and running with Pulseway MCP Server in 5 minutes!

## Prerequisites

- Python 3.10 or higher
- Pulseway RMM account with API access

## Installation

### Option 1: Automated Setup (Recommended)

```bash
# Clone the repository
git clone https://github.com/yourusername/pulseway-mcp-server.git
cd pulseway-mcp-server

# Run setup script
chmod +x setup.sh
./setup.sh
```

### Option 2: Manual Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/pulseway-mcp-server.git
cd pulseway-mcp-server

# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv pip install -e ".[dev]"

# Copy environment template
cp .env.example .env
```

## Configuration

### 1. Get Pulseway API Credentials

1. Log in to your Pulseway instance
2. Navigate to **Administration** → **Configuration** → **API Access**
3. Click **Create Token**
4. Configure the token:
   - Name: "MCP Server"
   - Access: All Companies (or select specific ones)
   - Note the **Token ID** and **Token Secret**

### 2. Configure Environment Variables

Edit `.env`:

```bash
PULSEWAY_SERVER_URL=https://your-instance.pulseway.com
PULSEWAY_TOKEN_ID=your_token_id_here
PULSEWAY_TOKEN_SECRET=your_token_secret_here
```

### 3. Test the Connection

```bash
# Run a quick test
uv run python -c "
import asyncio
from pulseway_mcp import PulsewayClient, PulsewayConfig
from dotenv import load_dotenv
import os

load_dotenv()

async def test():
    config = PulsewayConfig(
        server_url=os.getenv('PULSEWAY_SERVER_URL'),
        token_id=os.getenv('PULSEWAY_TOKEN_ID'),
        token_secret=os.getenv('PULSEWAY_TOKEN_SECRET')
    )
    async with PulsewayClient(config) as client:
        systems = await client.list_systems()
        print(f'✓ Connected! Found {len(systems)} systems.')

asyncio.run(test())
"
```

## Usage with Claude Desktop

### 1. Find Claude Desktop Config Location

- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **Linux**: `~/.config/Claude/claude_desktop_config.json`

### 2. Update Configuration

Add this to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "pulseway": {
      "command": "uv",
      "args": [
        "--directory",
        "/ABSOLUTE/PATH/TO/pulseway-mcp-server",
        "run",
        "pulseway-mcp-server"
      ],
      "env": {
        "PULSEWAY_SERVER_URL": "https://your-instance.pulseway.com",
        "PULSEWAY_TOKEN_ID": "your_token_id",
        "PULSEWAY_TOKEN_SECRET": "your_token_secret"
      }
    }
  }
}
```

**Important**: Replace `/ABSOLUTE/PATH/TO/` with the actual path to your cloned repository.

### 3. Restart Claude Desktop

Restart Claude Desktop to load the new MCP server.

### 4. Test It Out

Open Claude Desktop and try these commands:

```
List all my systems in Pulseway
```

```
Show me the details for system [system-id]
```

```
What notifications do I have for my servers?
```

## Example Interactions

### List Systems

**User**: "Show me all my online systems"

**Claude**: Uses the `list_systems` tool and returns:
```
I found 5 online systems:
1. Web-Server-01 (192.168.1.10) - Ubuntu 22.04
2. DB-Server-01 (192.168.1.20) - Windows Server 2022
...
```

### Get System Details

**User**: "Give me details on Web-Server-01"

**Claude**: Uses `get_system_details` and returns:
```
Web-Server-01 Details:
- Status: Online
- CPU Usage: 45%
- Memory Usage: 62%
- Disk Usage: 78%
- Uptime: 15 days
- Active Notifications: 2
```

### Check Notifications

**User**: "Show me active alerts"

**Claude**: Uses `get_system_notifications` and returns:
```
You have 3 active notifications:
1. High CPU Usage on Web-Server-01
2. Low Disk Space on DB-Server-02
3. Service Stopped on API-Server-01
```

## Troubleshooting

### "Cannot connect to Pulseway API"

**Check**:
- Is your `PULSEWAY_SERVER_URL` correct?
- Are your credentials valid?
- Is your IP whitelisted in Pulseway (if configured)?

**Test**:
```bash
curl -H "Authorization: Bearer TOKEN_ID:TOKEN_SECRET" \
     https://your-instance.pulseway.com/api/v1/systems
```

### "Module not found"

**Solution**:
```bash
# Reinstall dependencies
uv pip install -e .
```

### "Claude doesn't see the MCP server"

**Check**:
1. Is the path in `claude_desktop_config.json` correct?
2. Did you restart Claude Desktop?
3. Check Claude's logs:
   - **macOS**: `~/Library/Logs/Claude/mcp*.log`
   - **Windows**: `%APPDATA%\Claude\logs\mcp*.log`

### Enable Debug Logging

```bash
# Add to .env
LOG_LEVEL=DEBUG

# Or run directly
LOG_LEVEL=DEBUG uv run pulseway-mcp-server
```

## Next Steps

- 📖 Read [README.md](README.md) for full documentation
- 🔧 Check [MCP.md](MCP.md) to understand the protocol integration
- 🤝 See [CONTRIBUTING.md](CONTRIBUTING.md) to contribute
- 🐛 Report issues on [GitHub](https://github.com/yourusername/pulseway-mcp-server/issues)

## Development Commands

```bash
# Run tests
make test

# Format code
make format

# Run linting
make lint

# Type checking
make type-check

# Run all checks
make check-all

# Clean build artifacts
make clean
```

## Getting Help

- 📚 [Full Documentation](README.md)
- 💬 [GitHub Discussions](https://github.com/yourusername/pulseway-mcp-server/discussions)
- 🐛 [Report Issues](https://github.com/yourusername/pulseway-mcp-server/issues)

---

**Success!** You're now ready to use Pulseway with Claude through MCP! 🎉
