"""
Configuration settings for the Men's Circle Management Platform
"""
from functools import lru_cache
from pydantic_settings import BaseSettings
from pydantic import Field, ConfigDict
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    model_config = ConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore"  # Ignore extra environment variables
    )
    
    # Application settings
    app_name: str = "Men's Circle Management Platform"
    app_version: str = "0.1.0"
    environment: str = Field(default="development", alias="ENVIRONMENT")
    debug: bool = Field(default=True, alias="DEBUG")
    
    # Database settings - matching .env.example variable names
    database_url: str = Field(..., alias="DATABASE_URL")
    credentials_database_url: str = Field(..., alias="CREDS_DATABASE_URL")
    
    # Redis settings
    redis_url: str = Field(..., alias="REDIS_URL")
    
    # Security settings
    jwt_secret_key: str = Field(..., alias="JWT_SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", alias="JWT_ALGORITHM")
    access_token_expire_minutes: int = Field(default=30, alias="ACCESS_TOKEN_EXPIRE_MINUTES")
    refresh_token_expire_days: int = Field(default=7, alias="REFRESH_TOKEN_EXPIRE_DAYS")
    
    # Payment settings
    stripe_secret_key: str = Field(..., alias="STRIPE_SECRET_KEY")
    stripe_publishable_key: str = Field(..., alias="REACT_APP_STRIPE_PUBLISHABLE_KEY")
    stripe_webhook_secret: str = Field(..., alias="STRIPE_WEBHOOK_SECRET")
    
    # External service settings
    sendgrid_api_key: Optional[str] = Field(default=None, alias="SENDGRID_API_KEY")
    twilio_account_sid: Optional[str] = Field(default=None, alias="TWILIO_ACCOUNT_SID")
    twilio_auth_token: Optional[str] = Field(default=None, alias="TWILIO_AUTH_TOKEN")
    twilio_phone_number: Optional[str] = Field(default=None, alias="TWILIO_PHONE_NUMBER")
    
    # Google OAuth settings
    google_client_id: Optional[str] = Field(default=None, alias="GOOGLE_CLIENT_ID")
    google_client_secret: Optional[str] = Field(default=None, alias="GOOGLE_CLIENT_SECRET")
    
    # CORS settings
    cors_origins: list[str] = [
        "http://localhost:3000",  # Frontend development
        "http://localhost:80",    # Frontend production
        "https://localhost:3000", # HTTPS development
    ]


@lru_cache()
def get_settings() -> Settings:
    """Get cached application settings"""
    return Settings() 