"""Tests for the Pulseway API client."""

import pytest
from datetime import datetime
from pytest_httpx import HTTPXMock

from pulseway_mcp.client import PulsewayClient
from pulseway_mcp.models import (
    APIError,
    NotificationStatus,
    PulsewayConfig,
    SystemStatus,
)


@pytest.fixture
def config() -> PulsewayConfig:
    """Create a test configuration."""
    return PulsewayConfig(
        server_url="https://test.pulseway.com",
        token_id="test_token_id",
        token_secret="test_token_secret",
    )


@pytest.fixture
def mock_systems_response() -> list[dict]:
    """Mock systems API response."""
    return [
        {
            "id": "sys1",
            "name": "Server 1",
            "status": "online",
            "organization_id": "org1",
            "last_seen": "2025-01-01T12:00:00Z",
            "ip_address": "192.168.1.100",
            "operating_system": "Windows Server 2022",
        },
        {
            "id": "sys2",
            "name": "Server 2",
            "status": "offline",
            "organization_id": "org1",
            "last_seen": "2025-01-01T10:00:00Z",
            "ip_address": "192.168.1.101",
            "operating_system": "Ubuntu 22.04",
        },
    ]


@pytest.fixture
def mock_system_details_response() -> dict:
    """Mock system details API response."""
    return {
        "id": "sys1",
        "name": "Server 1",
        "status": "online",
        "organization_id": "org1",
        "last_seen": "2025-01-01T12:00:00Z",
        "ip_address": "192.168.1.100",
        "operating_system": "Windows Server 2022",
        "cpu_usage": 45.5,
        "memory_usage": 62.3,
        "disk_usage": 78.1,
        "uptime": 86400,
        "notifications_count": 3,
    }


@pytest.fixture
def mock_notifications_response() -> list[dict]:
    """Mock notifications API response."""
    return [
        {
            "id": "notif1",
            "title": "High CPU Usage",
            "message": "CPU usage exceeded 80%",
            "severity": "warning",
            "status": "active",
            "timestamp": "2025-01-01T12:00:00Z",
        },
        {
            "id": "notif2",
            "title": "Disk Space Low",
            "message": "Disk space below 20%",
            "severity": "error",
            "status": "acknowledged",
            "timestamp": "2025-01-01T11:00:00Z",
            "acknowledged_by": "admin@example.com",
            "acknowledged_at": "2025-01-01T11:30:00Z",
        },
    ]


@pytest.fixture
def mock_organizations_response() -> list[dict]:
    """Mock organizations API response."""
    return [
        {
            "id": "org1",
            "name": "Organization 1",
            "description": "Test organization",
        },
        {
            "id": "org2",
            "name": "Organization 2",
        },
    ]


class TestPulsewayClient:
    """Test cases for PulsewayClient."""

    @pytest.mark.asyncio
    async def test_list_systems(
        self, config: PulsewayConfig, httpx_mock: HTTPXMock, mock_systems_response: list[dict]
    ) -> None:
        """Test listing systems."""
        httpx_mock.add_response(
            url="https://test.pulseway.com/api/v1/systems",
            json={"systems": mock_systems_response},
        )

        async with PulsewayClient(config) as client:
            systems = await client.list_systems()

        assert len(systems) == 2
        assert systems[0].id == "sys1"
        assert systems[0].name == "Server 1"
        assert systems[0].status == SystemStatus.ONLINE
        assert systems[1].status == SystemStatus.OFFLINE

    @pytest.mark.asyncio
    async def test_list_systems_with_filters(
        self, config: PulsewayConfig, httpx_mock: HTTPXMock, mock_systems_response: list[dict]
    ) -> None:
        """Test listing systems with filters."""
        httpx_mock.add_response(
            url="https://test.pulseway.com/api/v1/systems?organization_id=org1&status=online",
            json={"systems": [mock_systems_response[0]]},
        )

        async with PulsewayClient(config) as client:
            systems = await client.list_systems(organization_id="org1", online_only=True)

        assert len(systems) == 1
        assert systems[0].status == SystemStatus.ONLINE

    @pytest.mark.asyncio
    async def test_get_system_details(
        self,
        config: PulsewayConfig,
        httpx_mock: HTTPXMock,
        mock_system_details_response: dict,
    ) -> None:
        """Test getting system details."""
        httpx_mock.add_response(
            url="https://test.pulseway.com/api/v1/systems/sys1",
            json=mock_system_details_response,
        )

        async with PulsewayClient(config) as client:
            details = await client.get_system_details("sys1")

        assert details.id == "sys1"
        assert details.name == "Server 1"
        assert details.cpu_usage == 45.5
        assert details.memory_usage == 62.3
        assert details.disk_usage == 78.1
        assert details.uptime == 86400
        assert details.notifications_count == 3

    @pytest.mark.asyncio
    async def test_get_system_notifications(
        self,
        config: PulsewayConfig,
        httpx_mock: HTTPXMock,
        mock_notifications_response: list[dict],
    ) -> None:
        """Test getting system notifications."""
        httpx_mock.add_response(
            url="https://test.pulseway.com/api/v1/systems/sys1/notifications",
            json={"notifications": mock_notifications_response},
        )

        async with PulsewayClient(config) as client:
            notifications = await client.get_system_notifications("sys1")

        assert len(notifications) == 2
        assert notifications[0].id == "notif1"
        assert notifications[0].title == "High CPU Usage"
        assert notifications[0].status == NotificationStatus.ACTIVE
        assert notifications[1].status == NotificationStatus.ACKNOWLEDGED

    @pytest.mark.asyncio
    async def test_get_system_notifications_with_filter(
        self,
        config: PulsewayConfig,
        httpx_mock: HTTPXMock,
        mock_notifications_response: list[dict],
    ) -> None:
        """Test getting system notifications with status filter."""
        httpx_mock.add_response(
            url="https://test.pulseway.com/api/v1/systems/sys1/notifications?status=active",
            json={"notifications": [mock_notifications_response[0]]},
        )

        async with PulsewayClient(config) as client:
            notifications = await client.get_system_notifications(
                "sys1", NotificationStatus.ACTIVE
            )

        assert len(notifications) == 1
        assert notifications[0].status == NotificationStatus.ACTIVE

    @pytest.mark.asyncio
    async def test_list_organizations(
        self,
        config: PulsewayConfig,
        httpx_mock: HTTPXMock,
        mock_organizations_response: list[dict],
    ) -> None:
        """Test listing organizations."""
        httpx_mock.add_response(
            url="https://test.pulseway.com/api/v1/organizations",
            json={"organizations": mock_organizations_response},
        )

        async with PulsewayClient(config) as client:
            organizations = await client.list_organizations()

        assert len(organizations) == 2
        assert organizations[0].id == "org1"
        assert organizations[0].name == "Organization 1"
        assert organizations[0].description == "Test organization"
        assert organizations[1].description is None

    @pytest.mark.asyncio
    async def test_api_error_handling(
        self, config: PulsewayConfig, httpx_mock: HTTPXMock
    ) -> None:
        """Test API error handling."""
        httpx_mock.add_response(
            url="https://test.pulseway.com/api/v1/systems",
            status_code=401,
            json={"error": "Unauthorized"},
        )

        async with PulsewayClient(config) as client:
            with pytest.raises(APIError) as exc_info:
                await client.list_systems()

        assert exc_info.value.status_code == 401

    @pytest.mark.asyncio
    async def test_health_check(self, config: PulsewayConfig, httpx_mock: HTTPXMock) -> None:
        """Test health check."""
        httpx_mock.add_response(
            url="https://test.pulseway.com/api/v1/health",
            json={"status": "ok"},
        )

        async with PulsewayClient(config) as client:
            result = await client.health_check()

        assert result is True

    @pytest.mark.asyncio
    async def test_health_check_failure(
        self, config: PulsewayConfig, httpx_mock: HTTPXMock
    ) -> None:
        """Test health check failure."""
        httpx_mock.add_response(
            url="https://test.pulseway.com/api/v1/health",
            status_code=503,
        )

        async with PulsewayClient(config) as client:
            result = await client.health_check()

        assert result is False
