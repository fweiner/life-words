"""Application configuration."""
import os
from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    # Supabase
    supabase_url: str
    supabase_secret_key: str

    # OpenAI
    openai_api_key: str

    # Google Cloud
    google_cloud_project: str
    google_application_credentials: str | None = None

    # Resend
    resend_api_key: str

    # AWS (for Amazon Polly TTS)
    aws_access_key_id: str | None = None
    aws_secret_access_key: str | None = None
    aws_region: str = "us-east-1"

    # Stripe
    stripe_secret_key: str | None = None
    stripe_webhook_secret: str | None = None
    stripe_monthly_price_id: str | None = None
    stripe_yearly_price_id: str | None = None

    # Application
    environment: str = "development"
    allowed_origins: str = "http://localhost:3000"
    admin_emails: str = "weiner@parrotsoftware.com"

    @property
    def cors_origins(self) -> List[str]:
        """Get CORS origins as a list."""
        # Support both comma and semicolon separators
        separator = ";" if ";" in self.allowed_origins else ","
        return [origin.strip() for origin in self.allowed_origins.split(separator)]

    model_config = {
        "env_file": ".env.local",
        "case_sensitive": False,
    }


# Global settings instance
settings = Settings()
