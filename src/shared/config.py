"""Application Configuration.

This module manages application configuration using Pydantic Settings.
Follows 12-factor app principles with config via environment variables.
"""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables.

    Attributes:
        environment: Application environment (development, staging, production).
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
        openai_api_key: OpenAI API key for LLM calls.
        use_mock_model: Whether to use mock model instead of real LLM.
        chroma_persist_directory: Directory for ChromaDB persistence.
        api_host: API host address.
        api_port: API port number.
    """

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=False
    )

    # Application Settings
    environment: str = Field(default="development", description="Application environment")
    log_level: str = Field(default="INFO", description="Logging level")

    # OpenAI Settings
    openai_api_key: str = Field(default="mock", description="OpenAI API key")
    use_mock_model: bool = Field(default=True, description="Use mock model for testing")

    # ChromaDB Settings
    chroma_persist_directory: str = Field(
        default="./data/chroma", description="ChromaDB persistence directory"
    )

    # API Settings
    api_host: str = Field(default="0.0.0.0", description="API host")
    api_port: int = Field(default=8000, description="API port")

    @property
    def is_development(self) -> bool:
        """Check if running in development environment.

        Returns:
            True if environment is development.
        """
        return self.environment.lower() == "development"

    @property
    def is_production(self) -> bool:
        """Check if running in production environment.

        Returns:
            True if environment is production.
        """
        return self.environment.lower() == "production"


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance.

    This function uses LRU cache to ensure settings are loaded only once.

    Returns:
        The application settings instance.
    """
    return Settings()
