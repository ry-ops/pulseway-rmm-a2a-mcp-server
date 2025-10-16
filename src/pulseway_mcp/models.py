"""Data models for Pulseway API responses."""

from datetime import datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


class NotificationStatus(str, Enum):
    """Notification status enum."""

    ACTIVE = "active"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"


class SystemStatus(str, Enum):
    """System status enum."""

    ONLINE = "online"
    OFFLINE = "offline"
    UNKNOWN = "unknown"


class MetricType(str, Enum):
    """Metric type enum."""

    CPU = "cpu"
    MEMORY = "memory"
    DISK = "disk"
    NETWORK = "network"


class Organization(BaseModel):
    """Pulseway organization model."""

    id: str
    name: str
    description: Optional[str] = None


class SystemInfo(BaseModel):
    """Basic system information model."""

    id: str
    name: str
    status: SystemStatus
    organization_id: str
    last_seen: Optional[datetime] = None
    ip_address: Optional[str] = None
    operating_system: Optional[str] = None


class SystemDetails(SystemInfo):
    """Detailed system information model."""

    cpu_usage: Optional[float] = Field(None, ge=0, le=100)
    memory_usage: Optional[float] = Field(None, ge=0, le=100)
    disk_usage: Optional[float] = Field(None, ge=0, le=100)
    uptime: Optional[int] = None  # in seconds
    installed_software: Optional[list[str]] = None
    notifications_count: Optional[int] = 0


class Notification(BaseModel):
    """System notification model."""

    id: str
    system_id: str
    title: str
    message: str
    severity: str
    status: NotificationStatus
    timestamp: datetime
    acknowledged_by: Optional[str] = None
    acknowledged_at: Optional[datetime] = None


class Metric(BaseModel):
    """Performance metric model."""

    timestamp: datetime
    value: float
    unit: str


class SystemMetrics(BaseModel):
    """System metrics collection model."""

    system_id: str
    metric_type: MetricType
    metrics: list[Metric]
    period_start: datetime
    period_end: datetime


class PulsewayConfig(BaseModel):
    """Pulseway API configuration model."""

    server_url: str
    token_id: str
    token_secret: str

    class Config:
        """Pydantic config."""

        frozen = True


class APIError(Exception):
    """Custom exception for Pulseway API errors."""

    def __init__(self, status_code: int, message: str, details: Optional[dict[str, Any]] = None):
        self.status_code = status_code
        self.message = message
        self.details = details or {}
        super().__init__(f"API Error {status_code}: {message}")
