"""Tests for the MCP server."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from pulseway_mcp.models import (
    Notification,
    NotificationStatus,
    Organization,
    SystemDetails,
    SystemInfo,
    SystemStatus,
)
from pulseway_mcp.server import call_tool, list_resources, list_tools


@pytest.fixture
def mock_client() -> MagicMock:
    """Create a mock Pulseway client."""
    client = MagicMock()
    client.__aenter__ = AsyncMock(return_value=client)
    client.__aexit__ = AsyncMock(return_value=None)
    return client


@pytest.fixture
def mock_systems() -> list[SystemInfo]:
    """Create mock system data."""
    return [
        SystemInfo(
            id="sys1",
            name="Server 1",
            status=SystemStatus.ONLINE,
            organization_id="org1",
            ip_address="192.168.1.100",
            operating_system="Windows Server 2022",
        ),
        SystemInfo(
            id="sys2",
            name="Server 2",
            status=SystemStatus.OFFLINE,
            organization_id="org1",
            ip_address="192.168.1.101",
            operating_system="Ubuntu 22.04",
        ),
    ]


@pytest.fixture
def mock_system_details() -> SystemDetails:
    """Create mock system details."""
    return SystemDetails(
        id="sys1",
        name="Server 1",
        status=SystemStatus.ONLINE,
        organization_id="org1",
        ip_address="192.168.1.100",
        operating_system="Windows Server 2022",
        cpu_usage=45.5,
        memory_usage=62.3,
        disk_usage=78.1,
        uptime=86400,
        notifications_count=3,
    )


@pytest.fixture
def mock_notifications() -> list[Notification]:
    """Create mock notifications."""
    from datetime import datetime

    return [
        Notification(
            id="notif1",
            system_id="sys1",
            title="High CPU Usage",
            message="CPU usage exceeded 80%",
            severity="warning",
            status=NotificationStatus.ACTIVE,
            timestamp=datetime.now(),
        ),
    ]


@pytest.fixture
def mock_organizations() -> list[Organization]:
    """Create mock organizations."""
    return [
        Organization(
            id="org1",
            name="Organization 1",
            description="Test organization",
        ),
    ]


class TestMCPServer:
    """Test cases for MCP server."""

    @pytest.mark.asyncio
    async def test_list_resources(self) -> None:
        """Test listing resources."""
        resources = await list_resources()
        
        assert len(resources) >= 2
        assert any(r.uri == "pulseway://docs/api" for r in resources)
        assert any(r.uri == "pulseway://systems" for r in resources)

    @pytest.mark.asyncio
    async def test_list_tools(self) -> None:
        """Test listing tools."""
        tools = await list_tools()
        
        assert len(tools) >= 5
        tool_names = [t.name for t in tools]
        assert "list_systems" in tool_names
        assert "get_system_details" in tool_names
        assert "get_system_notifications" in tool_names
        assert "list_organizations" in tool_names
        assert "get_system_metrics" in tool_names

    @pytest.mark.asyncio
    async def test_call_tool_list_systems(
        self, mock_client: MagicMock, mock_systems: list[SystemInfo]
    ) -> None:
        """Test calling list_systems tool."""
        mock_client.list_systems = AsyncMock(return_value=mock_systems)

        with patch("pulseway_mcp.server.get_client", return_value=mock_client):
            result = await call_tool("list_systems", {})

        assert len(result) == 1
        assert "sys1" in str(result[0].text)
        assert "sys2" in str(result[0].text)

    @pytest.mark.asyncio
    async def test_call_tool_list_systems_with_filters(
        self, mock_client: MagicMock, mock_systems: list[SystemInfo]
    ) -> None:
        """Test calling list_systems tool with filters."""
        mock_client.list_systems = AsyncMock(return_value=[mock_systems[0]])

        with patch("pulseway_mcp.server.get_client", return_value=mock_client):
            result = await call_tool(
                "list_systems",
                {"organization_id": "org1", "online_only": True},
            )

        assert len(result) == 1
        mock_client.list_systems.assert_called_once_with(
            organization_id="org1", online_only=True
        )

    @pytest.mark.asyncio
    async def test_call_tool_get_system_details(
        self, mock_client: MagicMock, mock_system_details: SystemDetails
    ) -> None:
        """Test calling get_system_details tool."""
        mock_client.get_system_details = AsyncMock(return_value=mock_system_details)

        with patch("pulseway_mcp.server.get_client", return_value=mock_client):
            result = await call_tool("get_system_details", {"system_id": "sys1"})

        assert len(result) == 1
        assert "sys1" in str(result[0].text)
        assert "45.5" in str(result[0].text)  # CPU usage

    @pytest.mark.asyncio
    async def test_call_tool_get_system_notifications(
        self, mock_client: MagicMock, mock_notifications: list[Notification]
    ) -> None:
        """Test calling get_system_notifications tool."""
        mock_client.get_system_notifications = AsyncMock(return_value=mock_notifications)

        with patch("pulseway_mcp.server.get_client", return_value=mock_client):
            result = await call_tool(
                "get_system_notifications",
                {"system_id": "sys1", "status": "active"},
            )

        assert len(result) == 1
        assert "notif1" in str(result[0].text)
        assert "High CPU Usage" in str(result[0].text)

    @pytest.mark.asyncio
    async def test_call_tool_list_organizations(
        self, mock_client: MagicMock, mock_organizations: list[Organization]
    ) -> None:
        """Test calling list_organizations tool."""
        mock_client.list_organizations = AsyncMock(return_value=mock_organizations)

        with patch("pulseway_mcp.server.get_client", return_value=mock_client):
            result = await call_tool("list_organizations", {})

        assert len(result) == 1
        assert "org1" in str(result[0].text)
        assert "Organization 1" in str(result[0].text)

    @pytest.mark.asyncio
    async def test_call_tool_unknown(self, mock_client: MagicMock) -> None:
        """Test calling unknown tool."""
        with patch("pulseway_mcp.server.get_client", return_value=mock_client):
            result = await call_tool("unknown_tool", {})

        assert len(result) == 1
        assert "Error" in str(result[0].text)

    @pytest.mark.asyncio
    async def test_call_tool_error_handling(self, mock_client: MagicMock) -> None:
        """Test error handling in tool calls."""
        mock_client.list_systems = AsyncMock(side_effect=Exception("API Error"))

        with patch("pulseway_mcp.server.get_client", return_value=mock_client):
            result = await call_tool("list_systems", {})

        assert len(result) == 1
        assert "Error" in str(result[0].text)
        assert "API Error" in str(result[0].text)
