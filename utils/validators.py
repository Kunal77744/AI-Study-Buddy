"""Input and file validation helpers for AI Study Buddy."""

from pathlib import Path

from config.settings import (
    ALLOWED_FILE_EXTENSIONS,
    MAX_FILE_SIZE_BYTES,
    MAX_FILE_SIZE_MB,
    MAX_QUIZ_QUESTIONS,
    MIN_QUIZ_QUESTIONS,
)
from utils.exceptions import ValidationError


def validate_non_empty_text(value: str, field_name: str = "Input") -> str:
    """Ensure text input is non-empty after stripping whitespace."""
    cleaned = value.strip() if isinstance(value, str) else ""
    if not cleaned:
        raise ValidationError(f"{field_name} cannot be empty.")
    return cleaned


def validate_question_count(count: int) -> int:
    """Ensure requested quiz question count is within allowed bounds."""
    if not isinstance(count, int) or isinstance(count, bool):
        raise ValidationError("Question count must be an integer.")
    if count < MIN_QUIZ_QUESTIONS or count > MAX_QUIZ_QUESTIONS:
        raise ValidationError(
            f"Question count must be between {MIN_QUIZ_QUESTIONS} and {MAX_QUIZ_QUESTIONS}."
        )
    return count


def validate_uploaded_file_metadata(filename: str, size_bytes: int) -> str:
    """Validate uploaded filename extension and size before processing.

    Returns the normalized lowercase extension without the leading dot.
    """
    if not filename or not filename.strip():
        raise ValidationError("Uploaded file must have a valid filename.")

    ext = Path(filename).suffix.lower().lstrip(".")
    if ext not in ALLOWED_FILE_EXTENSIONS:
        allowed = ", ".join(f".{e}" for e in ALLOWED_FILE_EXTENSIONS)
        raise ValidationError(
            f"Unsupported file type '.{ext or 'unknown'}'. Allowed types: {allowed}."
        )

    if size_bytes < 0:
        raise ValidationError("Invalid file size.")
    if size_bytes == 0:
        raise ValidationError(f"File '{filename}' is empty (0 bytes).")
    if size_bytes > MAX_FILE_SIZE_BYTES:
        raise ValidationError(
            f"File '{filename}' exceeds the {MAX_FILE_SIZE_MB} MB limit."
        )

    return ext
