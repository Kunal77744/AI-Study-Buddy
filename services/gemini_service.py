"""Google Gemini API integration using the official google-genai SDK."""

import logging
import re
import time
from collections.abc import Iterator
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
_TRANSIENT_STATUS_CODES = (408, 500, 502, 503, 504)


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


def _map_api_error(
    exc: genai_errors.APIError, model_id: str, attempt: int = 0, max_attempts: int = 1
) -> GeminiAPIError:
    """Log sanitized diagnostic details and return the appropriate GeminiAPIError."""
    safe_msg = _sanitize_error_message(exc.message)
    logger.error(
        "Gemini APIError (model=%s, attempt=%d/%d, code=%s, status=%s): %s",
        model_id,
        attempt + 1,
        max_attempts,
        exc.code,
        exc.status,
        safe_msg,
    )
    if _is_auth_api_error(exc):
        return GeminiAuthError(
            "Gemini API authentication failed. Please verify your API key."
        )
    if exc.code == 429 or (exc.status or "").upper() == "RESOURCE_EXHAUSTED":
        return GeminiRateLimitError(
            "Gemini API quota or rate limit exceeded. Please wait and try again."
        )
    if exc.code == 404 or (exc.status or "").upper() == "NOT_FOUND":
        return GeminiAPIError(
            f"Selected model '{model_id}' is unavailable or not found for this API key."
        )
    return GeminiAPIError(
        f"Gemini API request failed (status={exc.status or exc.code})."
    )


def _prepare_gemini_call(
    prompt: str,
    *,
    system_instruction: str | None,
    api_key: str | None,
    model_choice: str | None,
    timeout_seconds: int,
    response_mime_type: str | None = None,
    response_schema: Any = None,
) -> tuple[str, str, genai.Client, types.GenerateContentConfig | None]:
    """Validate inputs, resolve credentials/model, and build client + config."""
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

    config_kwargs: dict[str, Any] = {}
    if system_instruction:
        config_kwargs["system_instruction"] = system_instruction
    if response_mime_type:
        config_kwargs["response_mime_type"] = response_mime_type
    if response_schema is not None:
        config_kwargs["response_schema"] = response_schema

    config = types.GenerateContentConfig(**config_kwargs) if config_kwargs else None
    return cleaned_prompt, model_id, client, config


def generate_text(
    prompt: str,
    *,
    system_instruction: str | None = None,
    api_key: str | None = None,
    model_choice: str | None = None,
    timeout_seconds: int = API_TIMEOUT_SECONDS,
    max_retries: int = API_MAX_RETRIES,
    response_mime_type: str | None = None,
    response_schema: Any = None,
) -> str:
    """Generate text from Google Gemini using the official google-genai SDK.

    Raises:
        ValidationError: If prompt is empty.
        ConfigurationError: If API key is missing or model choice is invalid.
        GeminiAuthError: If authentication/permission fails.
        GeminiRateLimitError: If API quota or rate limit is exceeded.
        GeminiAPIError: For other API, timeout, or malformed-response errors.
    """
    cleaned_prompt, model_id, client, config = _prepare_gemini_call(
        prompt,
        system_instruction=system_instruction,
        api_key=api_key,
        model_choice=model_choice,
        timeout_seconds=timeout_seconds,
        response_mime_type=response_mime_type,
        response_schema=response_schema,
    )

    last_error: Exception | None = None
    total_attempts = max_retries + 1
    for attempt in range(total_attempts):
        try:
            response = client.models.generate_content(
                model=model_id,
                contents=cleaned_prompt,
                config=config,
            )
            return _extract_response_text(response)
        except genai_errors.APIError as exc:
            mapped = _map_api_error(exc, model_id, attempt, total_attempts)
            if exc.code in _TRANSIENT_STATUS_CODES:
                last_error = exc
                if attempt < max_retries:
                    time.sleep(API_RETRY_BACKOFF_SECONDS * (2**attempt))
                    continue
                raise GeminiAPIError(
                    f"Gemini API request timed out or was temporarily unavailable "
                    f"after {total_attempts} attempt(s)."
                ) from exc
            raise mapped from exc
        except (TimeoutError, ConnectionError) as exc:
            last_error = exc
            logger.warning(
                "Gemini network/timeout error (model=%s, attempt=%d/%d): %s",
                model_id,
                attempt + 1,
                total_attempts,
                type(exc).__name__,
            )
            if attempt < max_retries:
                time.sleep(API_RETRY_BACKOFF_SECONDS * (2**attempt))
                continue
            raise GeminiAPIError(
                f"Gemini API request timed out or was temporarily unavailable "
                f"after {total_attempts} attempt(s)."
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


def stream_text(
    prompt: str,
    *,
    system_instruction: str | None = None,
    api_key: str | None = None,
    model_choice: str | None = None,
    timeout_seconds: int = API_TIMEOUT_SECONDS,
    max_retries: int = API_MAX_RETRIES,
) -> Iterator[str]:
    """Stream text chunks from Google Gemini for low-latency UI rendering."""
    cleaned_prompt, model_id, client, config = _prepare_gemini_call(
        prompt,
        system_instruction=system_instruction,
        api_key=api_key,
        model_choice=model_choice,
        timeout_seconds=timeout_seconds,
    )

    total_attempts = max_retries + 1
    for attempt in range(total_attempts):
        yielded_any = False
        try:
            for chunk in client.models.generate_content_stream(
                model=model_id,
                contents=cleaned_prompt,
                config=config,
            ):
                text = getattr(chunk, "text", None)
                if isinstance(text, str) and text:
                    yielded_any = True
                    yield text
            if not yielded_any:
                logger.warning("Gemini stream completed with zero text chunks.")
                raise GeminiAPIError("The AI model returned an empty response.")
            return
        except genai_errors.APIError as exc:
            mapped = _map_api_error(exc, model_id, attempt, total_attempts)
            if not yielded_any and exc.code in _TRANSIENT_STATUS_CODES and attempt < max_retries:
                time.sleep(API_RETRY_BACKOFF_SECONDS * (2**attempt))
                continue
            raise mapped from exc
        except (TimeoutError, ConnectionError) as exc:
            logger.warning(
                "Gemini stream timeout/network error (model=%s, attempt=%d/%d): %s",
                model_id,
                attempt + 1,
                total_attempts,
                type(exc).__name__,
            )
            if not yielded_any and attempt < max_retries:
                time.sleep(API_RETRY_BACKOFF_SECONDS * (2**attempt))
                continue
            raise GeminiAPIError(
                "Gemini API stream timed out or lost connection."
            ) from exc
        except GeminiAPIError:
            raise
        except Exception as exc:
            logger.exception(
                "Unexpected Gemini stream error (model=%s, type=%s)",
                model_id,
                type(exc).__name__,
            )
            raise GeminiAPIError(
                f"Unexpected error communicating with Gemini ({type(exc).__name__})."
            ) from exc
