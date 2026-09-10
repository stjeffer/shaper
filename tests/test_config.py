"""Configuration behavior tests."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from shaper.config import ModelProvider, RuntimeProfile, Settings, SQLiteJournalMode


def test_given_local_profile_when_loaded_then_cloud_credentials_are_optional() -> None:
    # Act
    settings = Settings(_env_file=None)

    # Assert
    assert settings.model_provider is ModelProvider.FAKE
    assert settings.sqlite_journal_mode is SQLiteJournalMode.WAL


def test_given_azure_adapter_when_credentials_missing_then_validation_fails() -> None:
    # Act & Assert
    with pytest.raises(ValidationError, match="Azure OpenAI"):
        Settings(model_provider=ModelProvider.AZURE_OPENAI, _env_file=None)


def test_given_azure_managed_identity_when_selected_then_api_key_is_optional() -> None:
    settings = Settings(
        model_provider=ModelProvider.AZURE_OPENAI,
        azure_openai_endpoint="https://example.openai.azure.com",
        azure_openai_deployment="chat",
        azure_openai_embedding_deployment="embedding",
        azure_openai_use_managed_identity=True,
        _env_file=None,
    )

    assert settings.azure_openai_api_key is None


def test_given_production_profile_when_identity_missing_then_validation_fails() -> None:
    # Act & Assert
    with pytest.raises(ValidationError, match="identity settings"):
        Settings(profile=RuntimeProfile.PRODUCTION, _env_file=None)
