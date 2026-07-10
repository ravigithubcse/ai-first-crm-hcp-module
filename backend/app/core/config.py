# =============================================================================
# AI-First CRM HCP Module - Configuration Module
# =============================================================================
# Author      : Ravi Kumar
# Date        : 2026-07-09
# Version     : 1.0.0
# Description : Application configuration management using pydantic-settings
# Copyright (c) 2026. All rights reserved.
# =============================================================================

"""
Configuration management for the AI-First CRM HCP Module backend.
Handles environment variables and application settings.
"""

import os
from typing import List

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application Info
    app_name: str = "AI-First CRM HCP Module"
    app_version: str = "1.0.0"
    app_description: str = "AI-powered Healthcare Professional CRM System"
    debug: bool = True

    # Database
    database_url: str = "postgresql://postgres:postgres@localhost:5432/hcp_crm"

    # Groq LLM API
    groq_api_key: str = ""

    # CORS
    allowed_origins: str = "http://localhost:5173,http://localhost:3000"

    # Server
    host: str = "0.0.0.0"
    port: int = 8000

    @property
    def cors_origins(self) -> List[str]:
        """Parse allowed origins into a list."""
        return [origin.strip() for origin in self.allowed_origins.split(",")]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()