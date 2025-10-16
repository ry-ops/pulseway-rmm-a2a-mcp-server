"""Pulseway MCP Server implementation."""

import asyncio
import logging
import os
from typing import Any

from dotenv import load_dotenv
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Resource, TextContent, Tool

from .client import PulsewayClient
from .models import NotificationStatus, PulsewayConfig

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Initialize MCP server
app = Server("pulseway-mcp-server")

# Global client instance
_pulseway_client: PulsewayClient | None = None


def get_client() -> PulsewayClient:
    """Get or create the Pulseway client."""
    global _pulseway_client
    
    if _pulseway_client is None:
        config = PulsewayConfig(
            server_url=os.getenv("PULSEWAY_SERVER_URL", ""),
            token_id=os.getenv("PULSEWAY_TOKEN_ID", ""),
            token_secret=os.getenv("PULSEWAY_TOKEN_SECRET", ""),
        )
        
        if not all([config.server_url, config.token_id, config.token_secret]):
            raise ValueError(
                "Missing required environment variables: "
                "PULSEWAY_SERVER_URL, PULSEWAY_TOKEN_ID, PULSEWAY_TOKEN_SECRET"
            )
        
        _pulseway_client = PulsewayClient(config)
    
    return _pulseway_client


@app.list_resources()
async def list_resources() -> list[Resource]:
    """List available MCP resources.
    
    Returns:
        List of available resources
    """
    return [
        Resource(
            uri="pulseway://docs/api",
            name="Pulseway API Documentation",
            mimeType="text/plain",
            description="Documentation for the Pulseway RMM API",
        ),
        Resource(
            uri="pulseway://systems",
            name="Managed Systems",
            mimeType="application/json",
            description="List of all managed systems",
        ),
    ]


@app.read_resource()
async def read_resource(uri: str) -> str:
    """Read a resource by URI.
    
    Args:
        uri: Resource URI
        
    Returns:
        Resource content
    """
    if uri == "pulseway://docs/api":
        return """
# Pulseway RMM API Documentation

The Pulseway API provides programmatic access to your RMM platform.

## Authentication
- Uses token-based authentication
- Requires Token ID and Token Secret
- Tokens are configured in Administration -> Configuration -> API Access

## Available Endpoints
- GET /api/v1/organizations - List all organizations
- GET /api/v1/systems - List all systems
- GET /api/v1/systems/{id} - Get system details
- GET /api/v1/systems/{id}/notifications - Get system notifications
- GET /api/v1/systems/{id}/metrics/{type} - Get system metrics

## Rate Limits
- 1500 requests per hour per endpoint

For full documentation, visit: https://api.pulseway.com/
"""
    
    elif uri == "pulseway://systems":
        client = get_client()
        async with client:
            systems = await client.list_systems()
            return "\n".join([f"- {s.name} ({s.id}): {s.status}" for s in systems])
    
    raise ValueError(f"Unknown resource: {uri}")


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available MCP tools.
    
    Returns:
        List of available tools
    """
    return [
        Tool(
            name="list_systems",
            description="List all systems managed by Pulseway",
            inputSchema={
                "type": "object",
                "properties": {
                    "organization_id": {
                        "type": "string",
                        "description": "Optional organization ID to filter by",
                    },
                    "online_only": {
                        "type": "boolean",
                        "description": "If true, only return online systems",
                        "default": False,
                    },
                },
            },
        ),
        Tool(
            name="get_system_details",
            description="Get detailed information about a specific system",
            inputSchema={
                "type": "object",
                "properties": {
                    "system_id": {
                        "type": "string",
                        "description": "The ID of the system",
                    },
                },
                "required": ["system_id"],
            },
        ),
        Tool(
            name="get_system_notifications",
            description="Get notifications for a specific system",
            inputSchema={
                "type": "object",
                "properties": {
                    "system_id": {
                        "type": "string",
                        "description": "The ID of the system",
                    },
                    "status": {
                        "type": "string",
                        "enum": ["active", "acknowledged", "resolved"],
                        "description": "Filter by notification status",
                    },
                },
                "required": ["system_id"],
            },
        ),
        Tool(
            name="list_organizations",
            description="List all organizations in the Pulseway account",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
        Tool(
            name="get_system_metrics",
            description="Get performance metrics for a system",
            inputSchema={
                "type": "object",
                "properties": {
                    "system_id": {
                        "type": "string",
                        "description": "The ID of the system",
                    },
                    "metric_type": {
                        "type": "string",
                        "enum": ["cpu", "memory", "disk", "network"],
                        "description": "Type of metric to retrieve",
                        "default": "cpu",
                    },
                },
                "required": ["system_id"],
            },
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Call an MCP tool.
    
    Args:
        name: Tool name
        arguments: Tool arguments
        
    Returns:
        Tool result
    """
    client = get_client()
    
    try:
        async with client:
            if name == "list_systems":
                systems = await client.list_systems(
                    organization_id=arguments.get("organization_id"),
                    online_only=arguments.get("online_only", False),
                )
                result = {
                    "systems": [
                        {
                            "id": s.id,
                            "name": s.name,
                            "status": s.status.value,
                            "organization_id": s.organization_id,
                            "last_seen": s.last_seen.isoformat() if s.last_seen else None,
                            "ip_address": s.ip_address,
                            "operating_system": s.operating_system,
                        }
                        for s in systems
                    ],
                    "count": len(systems),
                }
                return [TextContent(type="text", text=str(result))]
            
            elif name == "get_system_details":
                system_id = arguments["system_id"]
                details = await client.get_system_details(system_id)
                result = {
                    "id": details.id,
                    "name": details.name,
                    "status": details.status.value,
                    "organization_id": details.organization_id,
                    "last_seen": details.last_seen.isoformat() if details.last_seen else None,
                    "ip_address": details.ip_address,
                    "operating_system": details.operating_system,
                    "cpu_usage": details.cpu_usage,
                    "memory_usage": details.memory_usage,
                    "disk_usage": details.disk_usage,
                    "uptime": details.uptime,
                    "notifications_count": details.notifications_count,
                }
                return [TextContent(type="text", text=str(result))]
            
            elif name == "get_system_notifications":
                system_id = arguments["system_id"]
                status = arguments.get("status")
                status_enum = NotificationStatus(status) if status else None
                
                notifications = await client.get_system_notifications(system_id, status_enum)
                result = {
                    "notifications": [
                        {
                            "id": n.id,
                            "title": n.title,
                            "message": n.message,
                            "severity": n.severity,
                            "status": n.status.value,
                            "timestamp": n.timestamp.isoformat(),
                            "acknowledged_by": n.acknowledged_by,
                            "acknowledged_at": (
                                n.acknowledged_at.isoformat() if n.acknowledged_at else None
                            ),
                        }
                        for n in notifications
                    ],
                    "count": len(notifications),
                }
                return [TextContent(type="text", text=str(result))]
            
            elif name == "list_organizations":
                organizations = await client.list_organizations()
                result = {
                    "organizations": [
                        {
                            "id": o.id,
                            "name": o.name,
                            "description": o.description,
                        }
                        for o in organizations
                    ],
                    "count": len(organizations),
                }
                return [TextContent(type="text", text=str(result))]
            
            elif name == "get_system_metrics":
                system_id = arguments["system_id"]
                metric_type = arguments.get("metric_type", "cpu")
                
                metrics = await client.get_system_metrics(system_id, metric_type)
                result = {
                    "system_id": metrics.system_id,
                    "metric_type": metrics.metric_type.value,
                    "period_start": metrics.period_start.isoformat(),
                    "period_end": metrics.period_end.isoformat(),
                    "metrics": [
                        {
                            "timestamp": m.timestamp.isoformat(),
                            "value": m.value,
                            "unit": m.unit,
                        }
                        for m in metrics.metrics
                    ],
                }
                return [TextContent(type="text", text=str(result))]
            
            else:
                raise ValueError(f"Unknown tool: {name}")
                
    except Exception as e:
        logger.error(f"Error calling tool {name}: {e}")
        return [TextContent(type="text", text=f"Error: {str(e)}")]


async def main() -> None:
    """Run the MCP server."""
    logger.info("Starting Pulseway MCP Server")
    
    # Verify configuration
    try:
        get_client()
        logger.info("Configuration validated successfully")
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        raise
    
    # Run the server
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())


def run() -> None:
    """Entry point for the server."""
    asyncio.run(main())


if __name__ == "__main__":
    run()
