"""Google Gemini API integration using the official google-genai SDK."""

import logging
import re
import time
from typing import Any

from google import genai
from google.genai import errors as genai_errors
from google.genai import types

from config.settings import (
    API_MAX_RETRIES,
    API_RETRY_BACKOFF_SECONDS,
    API_TIMEOUT_SECONDS,
    DEFAULT_MODEL_ID,
    MODEL_OPTIONS,
    resolve_api_key,
)
from utils.exceptions import (
    ConfigurationError,
    GeminiAPIError,
    GeminiAuthError,
    GeminiRateLimitError,
)
from utils.validators import validate_non_empty_text

logger = logging.getLogger("ai_study_buddy.gemini")
if not logger.handlers:
    _handler = logging.StreamHandler()
    _handler.setFormatter(
        logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    )
    logger.addHandler(_handler)
    logger.setLevel(logging.INFO)
    logger.propagate = False

_SECRET_PATTERN = re.compile(r"(AIza[0-9A-Za-z\-_]{10,}|key=[^&\s]+)")


def _sanitize_error_message(message: str | None) -> str:
    """Redact any accidental key-like tokens from diagnostic log messages."""
    if not message:
        return ""
    return _SECRET_PATTERN.sub("[REDACTED]", str(message))


def resolve_model_id(model_choice: str | None) -> str:
    """Map a UI model label or raw model ID to an exact Gemini model ID.

    Never silently substitutes one model for another.
    """
    if not model_choice or not model_choice.strip():
        return DEFAULT_MODEL_ID
    cleaned = model_choice.strip()
    if cleaned in MODEL_OPTIONS:
        return MODEL_OPTIONS[cleaned]
    if cleaned in MODEL_OPTIONS.values():
        return cleaned
    raise ConfigurationError(f"Unsupported AI model selection: '{cleaned}'.")


def _extract_response_text(response: Any) -> str:
    """Safely extract text from a google-genai GenerateContentResponse."""
    try:
        text = response.text
    except (ValueError, AttributeError, IndexError) as exc:
        logger.warning("Gemini response text extraction failed: %s", type(exc).__name__)
        raise GeminiAPIError(
            "The AI model returned an empty or safety-filtered response. "
            "Try rephrasing your prompt."
        ) from exc

    if not isinstance(text, str) or not text.strip():
        logger.warning("Gemini returned an empty response body.")
        raise GeminiAPIError("The AI model returned an empty response.")
    return text.strip()


def _is_auth_api_error(exc: genai_errors.APIError) -> bool:
    """Determine if a Gemini APIError represents invalid/unauthorized credentials."""
    if exc.code in (401, 403):
        return True
    status = (exc.status or "").upper()
    if status in ("UNAUTHENTICATED", "PERMISSION_DENIED"):
        return True
    msg = (exc.message or "").lower()
    return exc.code == 400 and "api key" in msg


def generate_text(
    prompt: str,
    *,
    system_instruction: str | None = None,
    api_key: str | None = None,
    model_choice: str | None = None,
    timeout_seconds: int = API_TIMEOUT_SECONDS,
    max_retries: int = API_MAX_RETRIES,
) -> str:
    """Generate text from Google Gemini using the official google-genai SDK.

    Raises:
        ValidationError: If prompt is empty.
        ConfigurationError: If API key is missing or model choice is invalid.
        GeminiAuthError: If authentication/permission fails.
        GeminiRateLimitError: If API quota or rate limit is exceeded.
        GeminiAPIError: For other API, timeout, or malformed-response errors.
    """
    cleaned_prompt = validate_non_empty_text(prompt, "Prompt")
    effective_key = resolve_api_key(api_key)
    if not effective_key:
        logger.error("Gemini API call aborted: GEMINI_API_KEY is not configured.")
        raise ConfigurationError(
            "Gemini API key is not configured. Add GEMINI_API_KEY to your .env file "
            "or Streamlit Secrets."
        )

    model_id = resolve_model_id(model_choice)
    client = genai.Client(
        api_key=effective_key,
        http_options=types.HttpOptions(timeout=timeout_seconds * 1000),
    )
    config = (
        types.GenerateContentConfig(system_instruction=system_instruction)
        if system_instruction
        else None
    )

    last_error: Exception | None = None
    for attempt in range(max_retries + 1):
        try:
            response = client.models.generate_content(
                model=model_id,
                contents=cleaned_prompt,
                config=config,
            )
            return _extract_response_text(response)
        except genai_errors.APIError as exc:
            safe_msg = _sanitize_error_message(exc.message)
            logger.error(
                "Gemini APIError (model=%s, attempt=%d/%d, code=%s, status=%s): %s",
                model_id,
                attempt + 1,
                max_retries + 1,
                exc.code,
                exc.status,
                safe_msg,
            )
            if _is_auth_api_error(exc):
                raise GeminiAuthError(
                    "Gemini API authentication failed. Please verify your API key."
                ) from exc
            if exc.code == 429 or (exc.status or "").upper() == "RESOURCE_EXHAUSTED":
                raise GeminiRateLimitError(
                    "Gemini API quota or rate limit exceeded. Please wait and try again."
                ) from exc
            if exc.code == 404 or (exc.status or "").upper() == "NOT_FOUND":
                raise GeminiAPIError(
                    f"Selected model '{model_id}' is unavailable or not found for this API key."
                ) from exc
            if exc.code in (408, 500, 502, 503, 504):
                last_error = exc
                if attempt < max_retries:
                    time.sleep(API_RETRY_BACKOFF_SECONDS * (2**attempt))
                    continue
                raise GeminiAPIError(
                    f"Gemini API request timed out or was temporarily unavailable "
                    f"after {max_retries + 1} attempt(s)."
                ) from exc
            raise GeminiAPIError(
                f"Gemini API request failed (status={exc.status or exc.code})."
            ) from exc
        except (TimeoutError, ConnectionError) as exc:
            last_error = exc
            logger.warning(
                "Gemini network/timeout error (model=%s, attempt=%d/%d): %s",
                model_id,
                attempt + 1,
                max_retries + 1,
                type(exc).__name__,
            )
            if attempt < max_retries:
                time.sleep(API_RETRY_BACKOFF_SECONDS * (2**attempt))
                continue
            raise GeminiAPIError(
                f"Gemini API request timed out or was temporarily unavailable "
                f"after {max_retries + 1} attempt(s)."
            ) from exc
        except GeminiAPIError:
            raise
        except Exception as exc:
            logger.exception(
                "Unexpected Gemini client error (model=%s, type=%s)",
                model_id,
                type(exc).__name__,
            )
            raise GeminiAPIError(
                f"Unexpected error communicating with Gemini ({type(exc).__name__})."
            ) from exc

    raise GeminiAPIError("Gemini API request failed.") from last_error
