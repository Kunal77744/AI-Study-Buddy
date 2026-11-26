"""Google Gemini API integration with explicit model selection, timeouts, and retries."""

import time
from typing import Any

import google.generativeai as genai
from google.api_core import exceptions as google_exceptions

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
    """Safely extract text from a Gemini response object."""
    try:
        text = response.text
    except (ValueError, AttributeError, IndexError) as exc:
        raise GeminiAPIError(
            "The AI model returned an empty or safety-filtered response. "
            "Try rephrasing your prompt."
        ) from exc

    if not isinstance(text, str) or not text.strip():
        raise GeminiAPIError("The AI model returned an empty response.")
    return text.strip()


def generate_text(
    prompt: str,
    *,
    system_instruction: str | None = None,
    api_key: str | None = None,
    model_choice: str | None = None,
    timeout_seconds: int = API_TIMEOUT_SECONDS,
    max_retries: int = API_MAX_RETRIES,
) -> str:
    """Generate text from Google Gemini with explicit model routing and controlled retries.

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
        raise ConfigurationError(
            "Gemini API key is not configured. Add GEMINI_API_KEY to your .env file "
            "or enter it in Developer Settings."
        )

    model_id = resolve_model_id(model_choice)
    genai.configure(api_key=effective_key)
    model = genai.GenerativeModel(
        model_name=model_id,
        system_instruction=system_instruction,
    )

    last_error: Exception | None = None
    for attempt in range(max_retries + 1):
        try:
            response = model.generate_content(
                cleaned_prompt,
                request_options={"timeout": timeout_seconds},
            )
            return _extract_response_text(response)
        except (
            google_exceptions.Unauthenticated,
            google_exceptions.PermissionDenied,
        ) as exc:
            raise GeminiAuthError(
                "Gemini API authentication failed. Please verify your API key."
            ) from exc
        except google_exceptions.ResourceExhausted as exc:
            raise GeminiRateLimitError(
                "Gemini API quota or rate limit exceeded. Please wait and try again."
            ) from exc
        except google_exceptions.NotFound as exc:
            raise GeminiAPIError(
                f"Selected model '{model_id}' is unavailable or not found for this API key."
            ) from exc
        except (
            google_exceptions.DeadlineExceeded,
            google_exceptions.ServiceUnavailable,
            TimeoutError,
            ConnectionError,
        ) as exc:
            last_error = exc
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
            raise GeminiAPIError(
                f"Unexpected error communicating with Gemini ({type(exc).__name__})."
            ) from exc

    raise GeminiAPIError("Gemini API request failed.") from last_error
