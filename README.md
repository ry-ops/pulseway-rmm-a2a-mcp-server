# Pulseway MCP Server

[![smithery badge](https://smithery.ai/badge/@username/pulseway-mcp-server)](https://smithery.ai/server/@username/pulseway-mcp-server)

A Model Context Protocol (MCP) server that provides integration with the Pulseway RMM (Remote Monitoring and Management) API. This server enables AI assistants to interact with Pulseway's monitoring and management capabilities.

## Features

- 🖥️ **System Management**: List and query managed systems
- 📊 **Monitoring**: Retrieve system status, metrics, and notifications
- 🔔 **Notifications**: Get system alerts and notifications
- 🏢 **Organization Management**: List and manage organizations
- 🔐 **Secure Authentication**: Token-based authentication with Pulseway API

## Installation

### Using `uv` (Recommended)

```bash
# Clone the repository
git clone https://github.com/yourusername/pulseway-mcp-server.git
cd pulseway-mcp-server

# Install using uv
uv pip install -e .
```

### Using pip

```bash
pip install pulseway-mcp-server
```

## Configuration

### Environment Variables

Create a `.env` file in your project root or set the following environment variables:

```bash
PULSEWAY_SERVER_URL=https://your-instance.pulseway.com
PULSEWAY_TOKEN_ID=your_token_id
PULSEWAY_TOKEN_SECRET=your_token_secret
```

### Obtaining Pulseway API Credentials

1. Log in to your Pulseway instance
2. Navigate to **Administration → Configuration → API Access**
3. Click **Create Token**
4. Enter a name and optional description
5. Set token validity dates
6. Choose access level (All Companies or Select Organizations)
7. Copy the **Token ID** and **Token Secret**

## Usage

### With Claude Desktop

Add this to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "pulseway": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/pulseway-mcp-server",
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

### Standalone

```bash
# Run the server
uv run pulseway-mcp-server

# Or with environment variables
PULSEWAY_SERVER_URL=https://your-instance.pulseway.com \
PULSEWAY_TOKEN_ID=your_token_id \
PULSEWAY_TOKEN_SECRET=your_token_secret \
uv run pulseway-mcp-server
```

## Available Tools

### 1. `list_systems`
Lists all systems managed by Pulseway.

**Parameters:**
- `organization_id` (optional): Filter by organization ID
- `online_only` (optional): Show only online systems

**Example:**
```json
{
  "organization_id": "12345",
  "online_only": true
}
```

### 2. `get_system_details`
Get detailed information about a specific system.

**Parameters:**
- `system_id` (required): The system ID

**Example:**
```json
{
  "system_id": "abc123"
}
```

### 3. `get_system_notifications`
Retrieve notifications for a specific system.

**Parameters:**
- `system_id` (required): The system ID
- `status` (optional): Filter by status (active, acknowledged, resolved)

**Example:**
```json
{
  "system_id": "abc123",
  "status": "active"
}
```

### 4. `list_organizations`
List all organizations in your Pulseway account.

**Example:**
```json
{}
```

### 5. `get_system_metrics`
Get performance metrics for a system.

**Parameters:**
- `system_id` (required): The system ID
- `metric_type` (optional): Type of metric (cpu, memory, disk, network)

**Example:**
```json
{
  "system_id": "abc123",
  "metric_type": "cpu"
}
```

## Resources

The server provides access to Pulseway documentation and system information through MCP resources:

- `pulseway://docs/api` - Pulseway API documentation
- `pulseway://systems` - List of managed systems

## Development

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/yourusername/pulseway-mcp-server.git
cd pulseway-mcp-server

# Install development dependencies
uv pip install -e ".[dev]"
```

### Running Tests

```bash
# Run tests
uv run pytest

# Run tests with coverage
uv run pytest --cov=pulseway_mcp --cov-report=html
```

### Code Quality

```bash
# Format code
uv run ruff format .

# Lint code
uv run ruff check .

# Type checking
uv run mypy src/pulseway_mcp
```

## Project Structure

```
pulseway-mcp-server/
├── src/
│   └── pulseway_mcp/
│       ├── __init__.py
│       ├── server.py          # Main MCP server implementation
│       ├── client.py          # Pulseway API client
│       └── models.py          # Data models
├── tests/
│   ├── __init__.py
│   ├── test_server.py
│   └── test_client.py
├── .github/
│   └── workflows/
│       └── ci.yml
├── pyproject.toml             # Project configuration
├── README.md
├── LICENSE
└── .gitignore
```

## API Rate Limits

The Pulseway API has rate limits:
- **Default**: 1500 requests per hour per endpoint
- Consider implementing caching for frequently accessed data

## Security Best Practices

1. **Never commit credentials**: Use environment variables or secure vaults
2. **Token rotation**: Regularly rotate your API tokens
3. **Minimal permissions**: Use tokens with the minimum required permissions
4. **Secure storage**: Store credentials securely in production

## Troubleshooting

### Connection Issues

If you're having trouble connecting:

1. Verify your server URL is correct
2. Check that your token ID and secret are valid
3. Ensure your IP is whitelisted (if configured in Pulseway)
4. Check firewall rules

### Authentication Errors

```
Error: Unauthorized (401)
```

- Verify your token ID and secret are correct
- Check that the token hasn't expired
- Ensure the token has appropriate permissions

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Links

- [Pulseway Website](https://www.pulseway.com/)
- [Pulseway API Documentation](https://api.pulseway.com/)
- [MCP Documentation](https://modelcontextprotocol.io/)
- [Model Context Protocol SDK](https://github.com/modelcontextprotocol/python-sdk)

## Support

For issues and questions:

- Open an issue on GitHub
- Check the [Pulseway Help Center](https://intercom.help/pulseway/)

## Acknowledgments

- Built with the [Model Context Protocol SDK](https://github.com/modelcontextprotocol/python-sdk)
- Powered by [Pulseway RMM API](https://www.pulseway.com/)
