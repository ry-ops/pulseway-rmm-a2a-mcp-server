# Model Context Protocol (MCP) Integration

This document explains how this server implements the Model Context Protocol and how it integrates with Pulseway's RMM API.

## What is MCP?

The Model Context Protocol (MCP) is an open protocol that standardizes how applications provide context to LLMs. It enables:

- **Standardized Integration**: A common protocol for connecting AI models to data sources
- **Tool Calling**: Structured way for LLMs to invoke functions
- **Resource Access**: Unified method for accessing external data
- **Composability**: Mix and match different MCP servers

## Architecture

```
┌─────────────────┐
│  Claude Desktop │
│   (or other     │
│   MCP client)   │
└────────┬────────┘
         │ MCP Protocol (stdio)
         │
┌────────▼────────────────┐
│  Pulseway MCP Server    │
│  ┌──────────────────┐   │
│  │  MCP Server      │   │
│  │  - Tools         │   │
│  │  - Resources     │   │
│  └────────┬─────────┘   │
│           │             │
│  ┌────────▼─────────┐   │
│  │  Pulseway Client │   │
│  └────────┬─────────┘   │
└───────────┼─────────────┘
            │ HTTPS/REST
            │
┌───────────▼─────────────┐
│   Pulseway RMM API      │
│   (api.pulseway.com)    │
└─────────────────────────┘
```

## Communication Flow

### 1. Client Initialization

```python
# Server announces capabilities
{
  "protocolVersion": "0.1.0",
  "capabilities": {
    "tools": true,
    "resources": true
  }
}
```

### 2. Tool Discovery

Client requests available tools:

```python
# list_tools() response
[
  {
    "name": "list_systems",
    "description": "List all systems managed by Pulseway",
    "inputSchema": {
      "type": "object",
      "properties": {
        "organization_id": {"type": "string"},
        "online_only": {"type": "boolean"}
      }
    }
  },
  # ... more tools
]
```

### 3. Tool Invocation

Client calls a tool:

```python
# Request
{
  "name": "list_systems",
  "arguments": {
    "organization_id": "org123",
    "online_only": true
  }
}

# Response
{
  "systems": [
    {
      "id": "sys1",
      "name": "Server 1",
      "status": "online",
      ...
    }
  ],
  "count": 1
}
```

## Server Components

### 1. Tools

Tools are functions that the LLM can invoke. Each tool has:

- **Name**: Unique identifier
- **Description**: What the tool does
- **Input Schema**: JSON Schema for parameters
- **Handler**: Async function that executes the tool

#### Example Tool Definition

```python
Tool(
    name="get_system_details",
    description="Get detailed information about a specific system",
    inputSchema={
        "type": "object",
        "properties": {
            "system_id": {
                "type": "string",
                "description": "The ID of the system"
            }
        },
        "required": ["system_id"]
    }
)
```

#### Tool Handler

```python
@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    if name == "get_system_details":
        client = get_client()
        async with client:
            details = await client.get_system_details(
                arguments["system_id"]
            )
            return [TextContent(
                type="text",
                text=str(details.model_dump())
            )]
```

### 2. Resources

Resources provide access to data and documentation:

```python
@app.list_resources()
async def list_resources() -> list[Resource]:
    return [
        Resource(
            uri="pulseway://docs/api",
            name="Pulseway API Documentation",
            mimeType="text/plain",
            description="Documentation for the Pulseway RMM API"
        )
    ]
```

### 3. Prompts (Future)

Prompts are reusable message templates for common tasks.

## Pulseway API Integration

### Authentication

```python
# Token-based authentication
headers = {
    "Authorization": f"Bearer {token_id}:{token_secret}",
    "Content-Type": "application/json"
}
```

### API Client

The `PulsewayClient` class handles all API interactions:

```python
async with PulsewayClient(config) as client:
    # List systems
    systems = await client.list_systems()
    
    # Get system details
    details = await client.get_system_details(system_id)
    
    # Get notifications
    notifications = await client.get_system_notifications(system_id)
```

### Error Handling

```python
try:
    data = await client._request("GET", "/systems")
except APIError as e:
    logger.error(f"API error {e.status_code}: {e.message}")
    # Return error to client
    return [TextContent(type="text", text=f"Error: {e.message}")]
```

## Data Flow

### Example: Listing Systems

1. **User asks Claude**: "Show me all online systems"

2. **Claude calls MCP tool**:
   ```json
   {
     "name": "list_systems",
     "arguments": {"online_only": true}
   }
   ```

3. **MCP Server processes**:
   - Validates arguments
   - Creates Pulseway client
   - Calls `client.list_systems(online_only=True)`

4. **Pulseway API request**:
   ```
   GET /api/v1/systems?status=online
   Authorization: Bearer token_id:token_secret
   ```

5. **Pulseway API response**:
   ```json
   {
     "systems": [
       {"id": "sys1", "name": "Server 1", ...}
     ]
   }
   ```

6. **MCP Server transforms**:
   - Parses response
   - Creates SystemInfo models
   - Formats for Claude

7. **Claude receives**:
   ```
   Found 1 online system:
   - Server 1 (sys1): online, last seen 2 minutes ago
   ```

## Configuration

### Environment Variables

```bash
PULSEWAY_SERVER_URL=https://your-instance.pulseway.com
PULSEWAY_TOKEN_ID=your_token_id
PULSEWAY_TOKEN_SECRET=your_token_secret
```

### Claude Desktop Config

```json
{
  "mcpServers": {
    "pulseway": {
      "command": "uv",
      "args": ["--directory", "/path/to/server", "run", "pulseway-mcp-server"],
      "env": {
        "PULSEWAY_SERVER_URL": "...",
        "PULSEWAY_TOKEN_ID": "...",
        "PULSEWAY_TOKEN_SECRET": "..."
      }
    }
  }
}
```

## Security Considerations

### 1. Credential Management

- ✅ Never commit credentials to git
- ✅ Use environment variables
- ✅ Support `.env` files for development
- ✅ Document credential rotation

### 2. API Access

- ✅ Use HTTPS for all API calls
- ✅ Validate SSL certificates
- ✅ Implement timeout handling
- ✅ Rate limit awareness

### 3. Input Validation

- ✅ Validate all tool arguments
- ✅ Sanitize user input
- ✅ Use Pydantic models for type safety
- ✅ Handle edge cases

### 4. Error Handling

- ✅ Don't expose sensitive data in errors
- ✅ Log errors securely
- ✅ Return user-friendly messages
- ✅ Handle API failures gracefully

## Testing

### Unit Tests

```python
@pytest.mark.asyncio
async def test_list_systems(mock_client):
    mock_client.list_systems = AsyncMock(return_value=[...])
    
    result = await call_tool("list_systems", {})
    
    assert len(result) == 1
    assert "sys1" in str(result[0].text)
```

### Integration Tests

```python
@pytest.mark.asyncio
async def test_api_integration(config):
    async with PulsewayClient(config) as client:
        systems = await client.list_systems()
        assert len(systems) > 0
```

### Mocking

Use `pytest-httpx` for HTTP mocking:

```python
def test_with_mock(httpx_mock):
    httpx_mock.add_response(
        url="https://api.pulseway.com/systems",
        json={"systems": [...]}
    )
```

## Extending the Server

### Adding a New Tool

1. **Define the tool**:
   ```python
   Tool(
       name="your_new_tool",
       description="...",
       inputSchema={...}
   )
   ```

2. **Implement the handler**:
   ```python
   elif name == "your_new_tool":
       # Implementation
       return [TextContent(type="text", text=result)]
   ```

3. **Add client method**:
   ```python
   async def your_new_method(self, ...):
       data = await self._request("GET", "/endpoint")
       return YourModel(**data)
   ```

4. **Add tests**:
   ```python
   async def test_your_new_tool():
       # Test implementation
   ```

### Adding a New Resource

```python
Resource(
    uri="pulseway://your/resource",
    name="Resource Name",
    mimeType="application/json",
    description="..."
)
```

## Best Practices

1. **Async/Await**: Use async for all I/O operations
2. **Type Safety**: Use type hints and Pydantic models
3. **Error Handling**: Catch and handle all exceptions
4. **Logging**: Log important events and errors
5. **Testing**: Write comprehensive tests
6. **Documentation**: Document all public APIs
7. **Security**: Never expose credentials
8. **Performance**: Cache when appropriate

## Troubleshooting

### Connection Issues

```python
# Check connectivity
async with client:
    is_healthy = await client.health_check()
    if not is_healthy:
        logger.error("Cannot connect to Pulseway API")
```

### Authentication Errors

```python
# Verify credentials
config = PulsewayConfig(
    server_url=os.getenv("PULSEWAY_SERVER_URL"),
    token_id=os.getenv("PULSEWAY_TOKEN_ID"),
    token_secret=os.getenv("PULSEWAY_TOKEN_SECRET")
)

if not all([config.server_url, config.token_id, config.token_secret]):
    raise ValueError("Missing required credentials")
```

### Debug Logging

```bash
# Enable debug logging
export LOG_LEVEL=DEBUG
uv run pulseway-mcp-server
```

## Resources

- [MCP Documentation](https://modelcontextprotocol.io/)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [Pulseway API Docs](https://api.pulseway.com/)
- [Project Repository](https://github.com/yourusername/pulseway-mcp-server)
