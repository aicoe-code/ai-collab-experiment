"""CDOS application configuration.

Implements: TR-005 (Configuration Management)
Uses Pydantic Settings for type-safe, validated configuration
loaded from environment variables.
"""

from __future__ import annotations

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application-wide configuration.

    Values are loaded from environment variables (prefixed CDOS_).
    """

    app_name: str = Field(
        default="CDOS", description="Application name"
    )
    app_version: str = Field(
        default="1.0.0", description="Application version"
    )
    debug: bool = Field(
        default=False, description="Enable debug mode"
    )
    log_level: str = Field(
        default="INFO", description="Logging level"
    )

    # Database
    database_url: str = Field(
        default="postgresql+asyncpg://cdos:cdos@localhost:5432/cdos",
        description="Async PostgreSQL connection string",
    )

    # Kafka
    kafka_bootstrap_servers: str = Field(
        default="localhost:9092",
        description="Kafka broker addresses (comma-separated)",
    )
    kafka_schema_registry_url: str = Field(
        default="http://localhost:8081",
        description="Confluent Schema Registry URL",
    )
    kafka_topic_prefix: str = Field(
        default="cdos",
        description="Prefix for all Kafka topics",
    )

    # External Systems
    edc_base_url: str = Field(
        default="https://edc.example.com/api",
        description="EDC system base URL",
    )
    edc_api_key: str = Field(
        default="", description="EDC system API key"
    )
    lims_base_url: str = Field(
        default="https://lims.example.com/api",
        description="LIMS system base URL",
    )
    lims_api_key: str = Field(
        default="", description="LIMS system API key"
    )
    safety_base_url: str = Field(
        default="https://safety.example.com/api",
        description="Safety system base URL",
    )
    safety_api_key: str = Field(
        default="", description="Safety system API key"
    )

    # Security
    jwt_secret_key: str = Field(
        default="change-me-in-production",
        description="JWT signing secret",
    )
    jwt_algorithm: str = Field(
        default="HS256", description="JWT algorithm"
    )
    jwt_expiration_minutes: int = Field(
        default=30, description="JWT token lifetime in minutes"
    )

    model_config = {"env_prefix": "CDOS_", "env_file": ".env", "extra": "ignore"}


@lru_cache
def get_settings() -> Settings:
    """Return cached singleton Settings instance."""
    return Settings()
