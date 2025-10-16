"""Pulseway RMM API client."""

import logging
from datetime import datetime
from typing import Any, Optional

import httpx

from .models import (
    APIError,
    Notification,
    NotificationStatus,
    Organization,
    PulsewayConfig,
    SystemDetails,
    SystemInfo,
    SystemMetrics,
    SystemStatus,
)

logger = logging.getLogger(__name__)


class PulsewayClient:
    """Client for interacting with the Pulseway RMM API."""

    def __init__(self, config: PulsewayConfig) -> None:
        """Initialize the Pulseway client.

        Args:
            config: Pulseway configuration with credentials
        """
        self.config = config
        self.base_url = config.server_url.rstrip("/")
        self._client: Optional[httpx.AsyncClient] = None

    async def __aenter__(self) -> "PulsewayClient":
        """Async context manager entry."""
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={
                "Authorization": f"Bearer {self.config.token_id}:{self.config.token_secret}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            timeout=30.0,
        )
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit."""
        if self._client:
            await self._client.aclose()

    @property
    def client(self) -> httpx.AsyncClient:
        """Get the HTTP client."""
        if self._client is None:
            raise RuntimeError("Client not initialized. Use async context manager.")
        return self._client

    async def _request(
        self, method: str, endpoint: str, **kwargs: Any
    ) -> dict[str, Any] | list[Any]:
        """Make an HTTP request to the Pulseway API.

        Args:
            method: HTTP method
            endpoint: API endpoint
            **kwargs: Additional request parameters

        Returns:
            Response data

        Raises:
            APIError: If the request fails
        """
        url = f"/api/v1{endpoint}"
        logger.debug(f"Making {method} request to {url}")

        try:
            response = await self.client.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error {e.response.status_code}: {e.response.text}")
            raise APIError(
                status_code=e.response.status_code,
                message=str(e),
                details={"response": e.response.text},
            )
        except httpx.RequestError as e:
            logger.error(f"Request error: {e}")
            raise APIError(status_code=0, message=f"Request failed: {e}")

    async def list_organizations(self) -> list[Organization]:
        """List all organizations.

        Returns:
            List of organizations
        """
        data = await self._request("GET", "/organizations")
        
        # Handle both dict and list responses
        if isinstance(data, dict):
            orgs = data.get("organizations", [])
        else:
            orgs = data
            
        return [
            Organization(
                id=org.get("id", ""),
                name=org.get("name", "Unknown"),
                description=org.get("description"),
            )
            for org in orgs
        ]

    async def list_systems(
        self, organization_id: Optional[str] = None, online_only: bool = False
    ) -> list[SystemInfo]:
        """List all systems.

        Args:
            organization_id: Optional organization ID to filter by
            online_only: If True, only return online systems

        Returns:
            List of systems
        """
        params: dict[str, Any] = {}
        if organization_id:
            params["organization_id"] = organization_id
        if online_only:
            params["status"] = "online"

        data = await self._request("GET", "/systems", params=params)
        
        # Handle both dict and list responses
        if isinstance(data, dict):
            systems = data.get("systems", [])
        else:
            systems = data

        return [
            SystemInfo(
                id=system.get("id", ""),
                name=system.get("name", "Unknown"),
                status=SystemStatus(system.get("status", "unknown")),
                organization_id=system.get("organization_id", ""),
                last_seen=self._parse_datetime(system.get("last_seen")),
                ip_address=system.get("ip_address"),
                operating_system=system.get("operating_system"),
            )
            for system in systems
        ]

    async def get_system_details(self, system_id: str) -> SystemDetails:
        """Get detailed information about a system.

        Args:
            system_id: System ID

        Returns:
            Detailed system information
        """
        data = await self._request("GET", f"/systems/{system_id}")

        return SystemDetails(
            id=data.get("id", system_id),
            name=data.get("name", "Unknown"),
            status=SystemStatus(data.get("status", "unknown")),
            organization_id=data.get("organization_id", ""),
            last_seen=self._parse_datetime(data.get("last_seen")),
            ip_address=data.get("ip_address"),
            operating_system=data.get("operating_system"),
            cpu_usage=data.get("cpu_usage"),
            memory_usage=data.get("memory_usage"),
            disk_usage=data.get("disk_usage"),
            uptime=data.get("uptime"),
            installed_software=data.get("installed_software"),
            notifications_count=data.get("notifications_count", 0),
        )

    async def get_system_notifications(
        self, system_id: str, status: Optional[NotificationStatus] = None
    ) -> list[Notification]:
        """Get notifications for a system.

        Args:
            system_id: System ID
            status: Optional status filter

        Returns:
            List of notifications
        """
        params: dict[str, Any] = {}
        if status:
            params["status"] = status.value

        data = await self._request("GET", f"/systems/{system_id}/notifications", params=params)
        
        # Handle both dict and list responses
        if isinstance(data, dict):
            notifications = data.get("notifications", [])
        else:
            notifications = data

        return [
            Notification(
                id=notif.get("id", ""),
                system_id=system_id,
                title=notif.get("title", ""),
                message=notif.get("message", ""),
                severity=notif.get("severity", "info"),
                status=NotificationStatus(notif.get("status", "active")),
                timestamp=self._parse_datetime(notif.get("timestamp")) or datetime.now(),
                acknowledged_by=notif.get("acknowledged_by"),
                acknowledged_at=self._parse_datetime(notif.get("acknowledged_at")),
            )
            for notif in notifications
        ]

    async def get_system_metrics(
        self, system_id: str, metric_type: str = "cpu"
    ) -> SystemMetrics:
        """Get performance metrics for a system.

        Args:
            system_id: System ID
            metric_type: Type of metric (cpu, memory, disk, network)

        Returns:
            System metrics
        """
        data = await self._request("GET", f"/systems/{system_id}/metrics/{metric_type}")

        # This is a placeholder implementation since the actual API structure may vary
        return SystemMetrics(
            system_id=system_id,
            metric_type=metric_type,  # type: ignore
            metrics=[],
            period_start=datetime.now(),
            period_end=datetime.now(),
        )

    @staticmethod
    def _parse_datetime(value: Optional[str | datetime]) -> Optional[datetime]:
        """Parse a datetime string or return existing datetime.

        Args:
            value: String or datetime to parse

        Returns:
            Parsed datetime or None
        """
        if value is None:
            return None
        if isinstance(value, datetime):
            return value
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        except (ValueError, AttributeError):
            logger.warning(f"Failed to parse datetime: {value}")
            return None

    async def health_check(self) -> bool:
        """Check if the API is accessible.

        Returns:
            True if API is accessible
        """
        try:
            await self._request("GET", "/health")
            return True
        except APIError:
            return False
