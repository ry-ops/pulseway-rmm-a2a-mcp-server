"""Pulseway MCP Server - Model Context Protocol server for Pulseway RMM API."""

from .client import PulsewayClient
from .models import (
    APIError,
    Notification,
    NotificationStatus,
    Organization,
    PulsewayConfig,
    SystemDetails,
    SystemInfo,
    SystemStatus,
)
from .server import main, run

__version__ = "0.1.0"

__all__ = [
    "APIError",
    "Notification",
    "NotificationStatus",
    "Organization",
    "PulsewayClient",
    "PulsewayConfig",
    "SystemDetails",
    "SystemInfo",
    "SystemStatus",
    "main",
    "run",
]
