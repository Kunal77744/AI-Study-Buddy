"""Shared Streamlit error rendering helpers for Study Buddy UI components."""

import streamlit as st

from utils.exceptions import (
    ConfigurationError,
    GeminiAPIError,
    GeminiRateLimitError,
    QuizParseError,
    StudyBuddyError,
)


def render_study_buddy_error(
    exc: Exception,
    *,
    generic_api_message: str = (
        "Could not complete the request right now. Please wait a moment and try again."
    ),
) -> None:
    """Display a user-friendly, consistent Streamlit error banner for StudyBuddyError."""
    if isinstance(exc, ConfigurationError):
        st.error(
            "AI Study Assistant is currently unavailable. Please try again later."
        )
    elif isinstance(exc, GeminiRateLimitError):
        st.error(
            "Too many requests right now. Please wait a moment and try again."
        )
    elif isinstance(exc, GeminiAPIError):
        st.error(generic_api_message)
    elif isinstance(exc, QuizParseError):
        st.error(
            "The generated quiz could not be formatted properly. Please try generating again."
        )
    elif isinstance(exc, StudyBuddyError):
        st.error(f"Notice: {exc}")
    else:
        raise exc
