"""
HR Audit Configuration Settings
Environment-based configuration using Pydantic Settings
"""

import os
from typing import List, Optional
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    # App Configuration
    APP_NAME: str = "HR Audit API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = Field(default=True, description="Enable debug mode")
    
    # Server Configuration
    HOST: str = Field(default="localhost", description="Server host")
    PORT: int = Field(default=8000, description="Server port")
    ALLOWED_HOSTS: List[str] = Field(
        default=["http://localhost:3000", "http://127.0.0.1:3000"],
        description="CORS allowed origins"
    )
    
    # Transaction Simulation
    TRANSACTION_INTERVAL: float = Field(
        default=2.0, description="Seconds between transactions"
    )
    NESSIE_API_KEY: Optional[str] = Field(
        default=None, description="Nessie API key from Capital One"
    )
    NESSIE_BASE_URL: str = Field(
        default="https://api.nessieisreal.com",
        description="Nessie API base URL"
    )
    
    # Database Configuration
    DATABASE_URL: str = Field(
        default="sqlite:///./hr_audit.db",
        description="Database connection URL"
    )
    REDIS_URL: str = Field(
        default="redis://localhost:6379/0",
        description="Redis connection URL"
    )
    
    # Machine Learning Configuration
    ANOMALY_THRESHOLD: float = Field(
        default=0.3, description="Anomaly detection threshold"
    )
    CONFIDENCE_THRESHOLD: float = Field(
        default=0.3, description="Minimum confidence score"
    )
    MODEL_UPDATE_INTERVAL: int = Field(
        default=3600, description="Model update interval in seconds"
    )
    
    # Logging Configuration
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")
    LOG_FILE: Optional[str] = Field(
        default=None, description="Log file path (None for console only)"
    )
    
    # Security Configuration
    SECRET_KEY: str = Field(
        default="your-secret-key-change-in-production",
        description="Application secret key"
    )
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default=30, description="Access token expiration time"
    )
    
    # Notification System Configuration
    ENABLE_NOTIFICATIONS: bool = Field(
        default=True, description="Enable anomaly notification system"
    )
    ENABLE_EMAIL_NOTIFICATIONS: bool = Field(
        default=True, description="Enable email notifications"
    )
    ENABLE_PHONE_NOTIFICATIONS: bool = Field(
        default=True, description="Enable phone call notifications"
    )
    
    # Email Configuration
    SMTP_SERVER: str = Field(
        default="smtp.gmail.com", description="SMTP server hostname"
    )
    SMTP_PORT: int = Field(
        default=587, description="SMTP server port"
    )
    SMTP_USERNAME: Optional[str] = Field(
        default=None, description="SMTP username/email"
    )
    SMTP_PASSWORD: Optional[str] = Field(
        default=None, description="SMTP password/app password"
    )
    EMAIL_FROM: Optional[str] = Field(
        default=None, description="From email address"
    )
    EMAIL_FROM_NAME: str = Field(
        default="HR Audit Security", description="From email display name"
    )
    
    # OpenAI API Configuration
    OPENAI_API_KEY: Optional[str] = Field(
        default=None, description="OpenAI API key"
    )
    OPENAI_MODEL: str = Field(
        default="gpt-3.5-turbo", description="OpenAI model to use (gpt-3.5-turbo, gpt-4, gpt-4-turbo)"
    )
    
    # Google Gemini API Configuration (Legacy - kept for backward compatibility)
    GEMINI_API_KEY: Optional[str] = Field(
        default=None, description="Google Gemini API key (deprecated)"
    )
    GEMINI_MODEL: str = Field(
        default="gemini-pro", description="Gemini model to use (deprecated)"
    )
    
    # Twilio Configuration
    TWILIO_ACCOUNT_SID: Optional[str] = Field(
        default=None, description="Twilio Account SID"
    )
    TWILIO_AUTH_TOKEN: Optional[str] = Field(
        default=None, description="Twilio Auth Token"
    )
    TWILIO_PHONE_NUMBER: Optional[str] = Field(
        default=None, description="Twilio phone number for outbound calls"
    )
    TWILIO_TTS_VOICE: str = Field(
        default="alice", description="Twilio TTS voice (alice, man, woman)"
    )
    TWILIO_WEBHOOK_URL: Optional[str] = Field(
        default=None, description="Base URL for Twilio webhooks"
    )
    
    # HR Audit Voice Integration
    PUBLIC_BASE_URL: Optional[str] = Field(
        default=None, description="Public URL for voice webhooks (ngrok in development)"
    )
    ENABLE_VOICE_CALLS: bool = Field(
        default=True, description="Enable integrated voice calling for fraud alerts"
    )
    
    # Notification Thresholds
    EMAIL_RISK_THRESHOLD: str = Field(
        default="low", description="Minimum risk level for email notifications"
    )
    PHONE_RISK_THRESHOLD: str = Field(
        default="high", description="Minimum risk level for phone notifications"
    )
    NOTIFICATION_COOLDOWN: int = Field(
        default=300, description="Cooldown between notifications for same customer (seconds)"
    )
    
    # Feature Flags
    ENABLE_MOCK_DATA: bool = Field(
        default=True, description="Enable mock transaction generation"
    )
    ENABLE_NESSIE_API: bool = Field(
        default=False, description="Enable Nessie API integration"
    )
    ENABLE_ADVANCED_ML: bool = Field(
        default=False, description="Enable advanced ML features"
    )
    ENABLE_MOBILE_PUSH: bool = Field(
        default=False, description="Enable mobile push notifications"
    )
    
    # Demo Configuration
    DEMO_MODE: bool = Field(
        default=True, description="Enable demo mode with preloaded scenarios"
    )
    DEMO_SCENARIOS_PATH: str = Field(
        default="./data/demo_scenarios.json",
        description="Path to demo scenarios file"
    )
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Validate configuration
        if self.ENABLE_NESSIE_API and not self.NESSIE_API_KEY:
            raise ValueError("NESSIE_API_KEY is required when ENABLE_NESSIE_API is True")
            
        # Validate notification configuration
        if self.ENABLE_EMAIL_NOTIFICATIONS:
            if not self.SMTP_USERNAME or not self.SMTP_PASSWORD:
                print("Warning: Email notifications enabled but SMTP credentials not configured")
            if not self.EMAIL_FROM:
                self.EMAIL_FROM = self.SMTP_USERNAME
                
        if self.ENABLE_NOTIFICATIONS and not self.OPENAI_API_KEY:
            print("Warning: Notifications enabled but OPENAI_API_KEY not configured. Fallback content will be used.")
            
        if self.ENABLE_PHONE_NOTIFICATIONS:
            if not self.TWILIO_ACCOUNT_SID or not self.TWILIO_AUTH_TOKEN:
                print("Warning: Phone notifications enabled but Twilio credentials not configured")
            if not self.TWILIO_PHONE_NUMBER:
                print("Warning: Phone notifications enabled but TWILIO_PHONE_NUMBER not configured")
            
        # Adjust transaction interval for demo mode
        if self.DEMO_MODE:
            self.TRANSACTION_INTERVAL = min(self.TRANSACTION_INTERVAL, 3.0)


# Create global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get application settings instance"""
    return settings