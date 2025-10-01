from pydantic_settings import BaseSettings
from typing import Optional
import os
from pathlib import Path

class Settings(BaseSettings):
    # Application settings
    app_name: str = "Governance-as-a-Service Backend"
    app_version: str = "1.0.0"
    debug: bool = True
    host: str = "0.0.0.0"
    port: int = 8000

    # Security settings
    secret_key: str = "your-secret-key-here"
    access_token_expire_minutes: int = 30

    # Database settings
    database_url: str = "sqlite:///./gaas.db"

    # Logging settings
    log_level: str = "INFO"
    log_file: str = "gaas_backend.log"

    # Policy management settings
    policy_storage_path: str = "./policies"
    max_policy_size_mb: int = 10

    # Compliance settings
    compliance_report_retention_days: int = 90

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

# Create a global settings instance
settings = Settings()

def get_settings() -> Settings:
    return settings
