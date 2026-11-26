"""Unit tests for config.settings and utils.validators."""

import pytest

from config.settings import resolve_api_key
from utils.exceptions import ValidationError
from utils.validators import (
    validate_non_empty_text,
    validate_question_count,
    validate_uploaded_file_metadata,
)


def test_resolve_api_key_prefers_override(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("GEMINI_API_KEY", "env-key-123")
    assert resolve_api_key("  override-key-456  ") == "override-key-456"


def test_resolve_api_key_falls_back_to_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("GEMINI_API_KEY", "env-key-123")
    assert resolve_api_key("") == "env-key-123"
    assert resolve_api_key(None) == "env-key-123"


def test_resolve_api_key_falls_back_to_st_secrets(monkeypatch: pytest.MonkeyPatch) -> None:
    import streamlit as st

    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.setattr(st, "secrets", {"GEMINI_API_KEY": "  secret-key-789  "})
    assert resolve_api_key("") == "secret-key-789"


def test_validate_non_empty_text_valid() -> None:
    assert validate_non_empty_text("  Binary Trees  ", "Topic") == "Binary Trees"


@pytest.mark.parametrize("raw", ["", "   ", "\n\t"])
def test_validate_non_empty_text_rejects_blank(raw: str) -> None:
    with pytest.raises(ValidationError, match="Topic cannot be empty"):
        validate_non_empty_text(raw, "Topic")


def test_validate_question_count_bounds() -> None:
    assert validate_question_count(1) == 1
    assert validate_question_count(10) == 10
    with pytest.raises(ValidationError):
        validate_question_count(0)
    with pytest.raises(ValidationError):
        validate_question_count(11)
    with pytest.raises(ValidationError):
        validate_question_count(True)  # type: ignore[arg-type]


def test_validate_uploaded_file_metadata_valid() -> None:
    assert validate_uploaded_file_metadata("notes.PDF", 1024) == "pdf"
    assert validate_uploaded_file_metadata("script.py", 512) == "py"


def test_validate_uploaded_file_metadata_rejects_invalid() -> None:
    with pytest.raises(ValidationError, match="Unsupported file type"):
        validate_uploaded_file_metadata("malware.exe", 100)
    with pytest.raises(ValidationError, match="empty"):
        validate_uploaded_file_metadata("empty.pdf", 0)
    with pytest.raises(ValidationError, match="limit"):
        validate_uploaded_file_metadata("huge.pdf", 11 * 1024 * 1024)
