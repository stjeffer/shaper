"""Typed runtime configuration with adapter-specific validation."""

from __future__ import annotations

from enum import StrEnum
from pathlib import Path

from pydantic import Field, SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class RuntimeProfile(StrEnum):
    """Supported runtime profiles."""

    LOCAL = "local"
    PRODUCTION = "production"


class ModelProvider(StrEnum):
    """Available model provider adapters."""

    FAKE = "fake"
    AZURE_OPENAI = "azure_openai"


class SQLiteJournalMode(StrEnum):
    """Supported SQLite journal modes."""

    WAL = "WAL"
    DELETE = "DELETE"


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="SHAPER_",
        extra="forbid",
        frozen=True,
    )

    profile: RuntimeProfile = RuntimeProfile.LOCAL
    database_path: Path = Path("shaper.db")
    sqlite_journal_mode: SQLiteJournalMode = SQLiteJournalMode.WAL
    upload_root: Path = Path("uploads")
    release_root: Path = Path("releases")
    collection_id: str | None = None
    model_provider: ModelProvider = ModelProvider.FAKE
    azure_openai_endpoint: str | None = None
    azure_openai_api_key: SecretStr | None = None
    azure_openai_deployment: str | None = None
    azure_openai_embedding_deployment: str | None = None
    azure_openai_use_managed_identity: bool = False
    oidc_issuer: str | None = None
    oidc_audience: str | None = None
    public_url: str | None = None
    clamd_host: str = "127.0.0.1"
    clamd_port: int = Field(default=3310, ge=1, le=65535)
    log_source_text: bool = Field(default=False, description="Unsafe outside isolated tests.")

    @model_validator(mode="after")
    def validate_selected_adapters(self) -> Settings:
        """Require credentials only for adapters that use them."""
        if self.model_provider is ModelProvider.AZURE_OPENAI:
            missing = [
                name
                for name, value in (
                    ("azure_openai_endpoint", self.azure_openai_endpoint),
                    ("azure_openai_deployment", self.azure_openai_deployment),
                    (
                        "azure_openai_embedding_deployment",
                        self.azure_openai_embedding_deployment,
                    ),
                )
                if value is None
            ]
            if not self.azure_openai_use_managed_identity and self.azure_openai_api_key is None:
                missing.append("azure_openai_api_key")
            if missing:
                raise ValueError(
                    "Azure OpenAI is selected but required settings are missing: "
                    + ", ".join(missing)
                )
        if self.profile is RuntimeProfile.PRODUCTION:
            missing = [
                name
                for name, value in (
                    ("oidc_issuer", self.oidc_issuer),
                    ("oidc_audience", self.oidc_audience),
                    ("public_url", self.public_url),
                    ("collection_id", self.collection_id),
                )
                if value is None
            ]
            if missing:
                raise ValueError(
                    "Production profile requires identity settings: " + ", ".join(missing)
                )
            if self.log_source_text:
                raise ValueError("Production profile cannot enable source text logging")
        return self
