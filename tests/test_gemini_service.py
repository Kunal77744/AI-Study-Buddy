"""Unit tests for services.gemini_service using mocked google-genai Client."""

import logging
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from google.genai import errors as genai_errors

from services.gemini_service import generate_text, resolve_model_id
from utils.exceptions import (
    ConfigurationError,
    GeminiAPIError,
    GeminiAuthError,
    GeminiRateLimitError,
    ValidationError,
)


def _make_api_error(code: int, status: str, message: str) -> genai_errors.APIError:
    return genai_errors.APIError(
        code,
        {"error": {"code": code, "status": status, "message": message}},
    )


def test_resolve_model_id_preserves_exact_models() -> None:
    assert resolve_model_id("gemini-2.5-flash (Recommended)") == "gemini-2.5-flash"
    assert resolve_model_id("gemini-1.5-flash") == "gemini-1.5-flash"
    assert resolve_model_id("gemini-1.5-pro") == "gemini-1.5-pro"


def test_resolve_model_id_rejects_unknown() -> None:
    with pytest.raises(ConfigurationError, match="Unsupported AI model"):
        resolve_model_id("unknown-model-99")


def test_generate_text_missing_key_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    with pytest.raises(ConfigurationError, match="not configured"):
        generate_text("Explain TCP/IP", api_key="")


def test_generate_text_empty_prompt_raises() -> None:
    with pytest.raises(ValidationError, match="Prompt cannot be empty"):
        generate_text("   ", api_key="fake-key")


def test_generate_text_success_and_explicit_model(monkeypatch: pytest.MonkeyPatch) -> None:
    mock_client = MagicMock()
    mock_client.models.generate_content.return_value = SimpleNamespace(text="  Hello student!  ")
    mock_client_cls = MagicMock(return_value=mock_client)

    monkeypatch.setattr("services.gemini_service.genai.Client", mock_client_cls)

    result = generate_text(
        "Explain DNS",
        system_instruction="Be concise",
        api_key="test-key",
        model_choice="gemini-1.5-pro",
        timeout_seconds=15,
    )

    assert result == "Hello student!"
    mock_client_cls.assert_called_once()
    call_kwargs = mock_client_cls.call_args.kwargs
    assert call_kwargs["api_key"] == "test-key"
    assert call_kwargs["http_options"].timeout == 15_000

    gen_kwargs = mock_client.models.generate_content.call_args.kwargs
    assert gen_kwargs["model"] == "gemini-1.5-pro"
    assert gen_kwargs["contents"] == "Explain DNS"
    assert gen_kwargs["config"].system_instruction == "Be concise"


def test_generate_text_auth_error_does_not_retry_and_redacts_logs(
    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    mock_client = MagicMock()
    mock_client.models.generate_content.side_effect = _make_api_error(
        400, "INVALID_ARGUMENT", "API key not valid: AIzaSyDummySecretKey12345"
    )
    monkeypatch.setattr(
        "services.gemini_service.genai.Client", MagicMock(return_value=mock_client)
    )

    with caplog.at_level(logging.ERROR, logger="ai_study_buddy.gemini"):
        with pytest.raises(GeminiAuthError, match="authentication failed"):
            generate_text("Hi", api_key="AIzaSyDummySecretKey12345", max_retries=2)

    assert mock_client.models.generate_content.call_count == 1
    assert "AIzaSyDummySecretKey12345" not in caplog.text
    assert "[REDACTED]" in caplog.text


def test_generate_text_rate_limit_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    mock_client = MagicMock()
    mock_client.models.generate_content.side_effect = _make_api_error(
        429, "RESOURCE_EXHAUSTED", "Quota exceeded"
    )
    monkeypatch.setattr(
        "services.gemini_service.genai.Client", MagicMock(return_value=mock_client)
    )

    with pytest.raises(GeminiRateLimitError, match="quota"):
        generate_text("Hi", api_key="key")


def test_generate_text_retries_on_transient_server_error_then_succeeds(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    mock_client = MagicMock()
    mock_client.models.generate_content.side_effect = [
        _make_api_error(503, "UNAVAILABLE", "Backend temporarily unavailable"),
        SimpleNamespace(text="Recovered response"),
    ]
    monkeypatch.setattr(
        "services.gemini_service.genai.Client", MagicMock(return_value=mock_client)
    )
    monkeypatch.setattr("services.gemini_service.time.sleep", MagicMock())

    result = generate_text("Hi", api_key="key", max_retries=1)
    assert result == "Recovered response"
    assert mock_client.models.generate_content.call_count == 2


def test_generate_text_not_found_does_not_fallback(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    mock_client = MagicMock()
    mock_client.models.generate_content.side_effect = _make_api_error(
        404, "NOT_FOUND", "Model not found"
    )
    monkeypatch.setattr(
        "services.gemini_service.genai.Client", MagicMock(return_value=mock_client)
    )

    with pytest.raises(GeminiAPIError, match="unavailable or not found"):
        generate_text("Hi", api_key="key", model_choice="gemini-1.5-pro")


def test_generate_text_empty_response_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    mock_client = MagicMock()
    mock_client.models.generate_content.return_value = SimpleNamespace(text="   ")
    monkeypatch.setattr(
        "services.gemini_service.genai.Client", MagicMock(return_value=mock_client)
    )

    with pytest.raises(GeminiAPIError, match="empty response"):
        generate_text("Hi", api_key="key")
