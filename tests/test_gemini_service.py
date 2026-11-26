"""Unit tests for services.gemini_service (all API calls mocked)."""

from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from google.api_core import exceptions as google_exceptions

from services.gemini_service import generate_text, resolve_model_id
from utils.exceptions import (
    ConfigurationError,
    GeminiAPIError,
    GeminiAuthError,
    GeminiRateLimitError,
    ValidationError,
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
    mock_model = MagicMock()
    mock_model.generate_content.return_value = SimpleNamespace(text="  Hello student!  ")
    mock_cls = MagicMock(return_value=mock_model)
    mock_configure = MagicMock()

    monkeypatch.setattr("services.gemini_service.genai.configure", mock_configure)
    monkeypatch.setattr("services.gemini_service.genai.GenerativeModel", mock_cls)

    result = generate_text(
        "Explain DNS",
        system_instruction="Be concise",
        api_key="test-key",
        model_choice="gemini-1.5-pro",
        timeout_seconds=15,
    )

    assert result == "Hello student!"
    mock_configure.assert_called_once_with(api_key="test-key")
    mock_cls.assert_called_once_with(
        model_name="gemini-1.5-pro", system_instruction="Be concise"
    )
    mock_model.generate_content.assert_called_once_with(
        "Explain DNS", request_options={"timeout": 15}
    )


def test_generate_text_auth_error_does_not_retry(monkeypatch: pytest.MonkeyPatch) -> None:
    mock_model = MagicMock()
    mock_model.generate_content.side_effect = google_exceptions.Unauthenticated("bad key")
    monkeypatch.setattr("services.gemini_service.genai.configure", MagicMock())
    monkeypatch.setattr(
        "services.gemini_service.genai.GenerativeModel", MagicMock(return_value=mock_model)
    )

    with pytest.raises(GeminiAuthError, match="authentication failed"):
        generate_text("Hi", api_key="bad-key", max_retries=2)
    assert mock_model.generate_content.call_count == 1


def test_generate_text_rate_limit_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    mock_model = MagicMock()
    mock_model.generate_content.side_effect = google_exceptions.ResourceExhausted("quota")
    monkeypatch.setattr("services.gemini_service.genai.configure", MagicMock())
    monkeypatch.setattr(
        "services.gemini_service.genai.GenerativeModel", MagicMock(return_value=mock_model)
    )

    with pytest.raises(GeminiRateLimitError, match="quota"):
        generate_text("Hi", api_key="key")


def test_generate_text_retries_on_timeout_then_succeeds(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    mock_model = MagicMock()
    mock_model.generate_content.side_effect = [
        google_exceptions.DeadlineExceeded("timeout"),
        SimpleNamespace(text="Recovered response"),
    ]
    monkeypatch.setattr("services.gemini_service.genai.configure", MagicMock())
    monkeypatch.setattr(
        "services.gemini_service.genai.GenerativeModel", MagicMock(return_value=mock_model)
    )
    monkeypatch.setattr("services.gemini_service.time.sleep", MagicMock())

    result = generate_text("Hi", api_key="key", max_retries=1)
    assert result == "Recovered response"
    assert mock_model.generate_content.call_count == 2


def test_generate_text_not_found_does_not_fallback(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    mock_model = MagicMock()
    mock_model.generate_content.side_effect = google_exceptions.NotFound("missing model")
    monkeypatch.setattr("services.gemini_service.genai.configure", MagicMock())
    monkeypatch.setattr(
        "services.gemini_service.genai.GenerativeModel", MagicMock(return_value=mock_model)
    )

    with pytest.raises(GeminiAPIError, match="unavailable or not found"):
        generate_text("Hi", api_key="key", model_choice="gemini-1.5-pro")
