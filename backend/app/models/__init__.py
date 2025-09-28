"""
FinancePulse Data Models
Pydantic models for transactions, anomalies, and API responses
"""

from datetime import datetime
from typing import Dict, List, Optional, Any
from enum import Enum

from pydantic import BaseModel, Field, ConfigDict


class TransactionType(str, Enum):
    """Transaction type enumeration"""
    PURCHASE = "purchase"
    WITHDRAWAL = "withdrawal"
    DEPOSIT = "deposit"
    TRANSFER = "transfer"
    PAYMENT = "payment"


class MerchantCategory(str, Enum):
    """Merchant category codes"""
    GROCERY = "grocery"
    RESTAURANT = "restaurant"
    GAS_STATION = "gas_station"
    RETAIL = "retail"
    ENTERTAINMENT = "entertainment"
    HEALTHCARE = "healthcare"
    TRAVEL = "travel"
    ONLINE = "online"
    ATM = "atm"
    UNKNOWN = "unknown"


class Transaction(BaseModel):
    """Transaction data model"""
    id: str = Field(..., description="Unique transaction ID")
    account_id: str = Field(..., description="Account identifier")
    customer_id: str = Field(..., description="Customer identifier")
    amount: float = Field(..., description="Transaction amount")
    type: TransactionType = Field(..., description="Transaction type")
    merchant_name: str = Field(..., description="Merchant name")
    merchant_category: MerchantCategory = Field(..., description="Merchant category")
    location: Optional[Dict[str, Any]] = Field(None, description="Transaction location")
    timestamp: datetime = Field(..., description="Transaction timestamp")
    description: Optional[str] = Field(None, description="Transaction description")
    
    # Additional context fields
    balance_before: Optional[float] = Field(None, description="Account balance before transaction")
    balance_after: Optional[float] = Field(None, description="Account balance after transaction")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")

    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat()
        }
    )


class AnomalyType(str, Enum):
    """Types of anomalies that can be detected"""
    UNUSUAL_AMOUNT = "unusual_amount"
    UNUSUAL_FREQUENCY = "unusual_frequency"
    UNUSUAL_LOCATION = "unusual_location"
    UNUSUAL_TIME = "unusual_time"
    UNUSUAL_MERCHANT = "unusual_merchant"
    VELOCITY_SPIKE = "velocity_spike"
    AMOUNT_PATTERN = "amount_pattern"
    GEOGRAPHIC_OUTLIER = "geographic_outlier"


class RiskLevel(str, Enum):
    """Risk level classification"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AnomalyResult(BaseModel):
    """Anomaly detection result"""
    is_anomaly: bool = Field(..., description="Whether transaction is anomalous")
    confidence_score: float = Field(..., description="Confidence score (0-1)")
    risk_level: RiskLevel = Field(..., description="Risk level classification")
    anomaly_types: List[AnomalyType] = Field(default=[], description="Types of anomalies detected")
    features: Dict[str, float] = Field(default={}, description="Feature values used in detection")
    explanation: Optional[str] = Field(None, description="Human-readable explanation")
    recommendations: List[str] = Field(default=[], description="Recommended actions")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Detection timestamp")

    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat()
        }
    )


class NotificationStatus(str, Enum):
    """Notification delivery status"""
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    CANCELLED = "cancelled"


class NotificationType(str, Enum):
    """Types of notifications"""
    EMAIL = "email"
    PHONE = "phone"
    SMS = "sms"
    PUSH = "push"


class CustomerContact(BaseModel):
    """Customer contact information"""
    customer_id: str = Field(..., description="Customer identifier")
    name: str = Field(..., description="Customer full name")
    email: Optional[str] = Field(None, description="Email address")
    phone: Optional[str] = Field(None, description="Phone number")
    preferred_contact_method: NotificationType = Field(
        default=NotificationType.EMAIL, description="Preferred contact method"
    )
    email_notifications_enabled: bool = Field(
        default=True, description="Email notifications enabled"
    )
    phone_notifications_enabled: bool = Field(
        default=True, description="Phone notifications enabled"
    )
    notification_threshold: RiskLevel = Field(
        default=RiskLevel.MEDIUM, description="Minimum risk level for notifications"
    )
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat()
        }
    )


class NotificationRecord(BaseModel):
    """Notification delivery record"""
    id: str = Field(..., description="Notification ID")
    customer_id: str = Field(..., description="Customer identifier")
    transaction_id: str = Field(..., description="Related transaction ID")
    notification_type: NotificationType = Field(..., description="Type of notification")
    status: NotificationStatus = Field(..., description="Delivery status")
    subject: Optional[str] = Field(None, description="Email subject or call topic")
    content: str = Field(..., description="Notification content")
    recipient: str = Field(..., description="Email address or phone number")
    risk_level: RiskLevel = Field(..., description="Risk level that triggered notification")
    sent_at: Optional[datetime] = Field(None, description="When notification was sent")
    delivered_at: Optional[datetime] = Field(None, description="When notification was delivered")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    retry_count: int = Field(default=0, description="Number of retry attempts")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat()
        }
    )


class NotificationSettings(BaseModel):
    """Notification system settings"""
    customer_id: str = Field(..., description="Customer identifier")
    email_enabled: bool = Field(default=True)
    phone_enabled: bool = Field(default=True)
    email_threshold: RiskLevel = Field(default=RiskLevel.MEDIUM)
    phone_threshold: RiskLevel = Field(default=RiskLevel.HIGH)
    cooldown_period: int = Field(default=300, description="Seconds between notifications")
    max_daily_notifications: int = Field(default=10)
    quiet_hours_start: Optional[int] = Field(None, description="Quiet hours start (24h format)")
    quiet_hours_end: Optional[int] = Field(None, description="Quiet hours end (24h format)")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat()
        }
    )


class APIResponse(BaseModel):
    """Base API response model"""
    success: bool = Field(True, description="Request success status")
    message: Optional[str] = Field(None, description="Response message")
    data: Optional[Any] = Field(None, description="Response data")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")

    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat()
        }
    )
