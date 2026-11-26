"""Centralized configuration and constants for AI Study Buddy."""

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()

APP_TITLE = "AI Study Buddy | IBM SkillsBuild Capstone"
APP_ICON = "🎓"
APP_VERSION = "2.5.1"

# Explicit model registry: display label -> exact Gemini model ID
MODEL_OPTIONS: dict[str, str] = {
    "gemini-3.8-flash (Recommended)": "gemini-3.8-flash",
    "gemini-2.5-flash": "gemini-2.5-flash",
    "gemini-1.5-flash": "gemini-1.5-flash",
    "gemini-1.5-pro": "gemini-1.5-pro",
}
DEFAULT_MODEL_LABEL = "gemini-3.8-flash (Recommended)"
DEFAULT_MODEL_ID = MODEL_OPTIONS[DEFAULT_MODEL_LABEL]

# Gemini API settings
API_TIMEOUT_SECONDS = 30
API_MAX_RETRIES = 2
API_RETRY_BACKOFF_SECONDS = 1.0

# Document upload & text processing limits
ALLOWED_FILE_EXTENSIONS: tuple[str, ...] = ("pdf", "txt", "md", "py", "json")
MAX_FILE_SIZE_MB = 10
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024
MAX_PDF_PAGES = 50
MAX_SUMMARY_INPUT_CHARS = 15_000
MIN_MEANINGFUL_TEXT_CHARS = 20

# Quiz generation limits
MIN_QUIZ_QUESTIONS = 1
MAX_QUIZ_QUESTIONS = 10
DEFAULT_QUIZ_QUESTIONS = 4
QUIZ_PASS_THRESHOLD_PCT = 75
QUIZ_DIFFICULTIES: tuple[str, ...] = ("Easy", "Medium", "Hard")

# Study Roadmap options
ROADMAP_DURATIONS: tuple[str, ...] = ("1 Week", "2 Weeks", "4 Weeks", "8 Weeks")
ROADMAP_LEVELS: tuple[str, ...] = ("Beginner", "Intermediate", "Advanced")


@dataclass(frozen=True)
class AppMetadata:
    """Project metadata displayed in sidebar and documentation tab."""

    title: str = "AI-Powered Study Buddy"
    author: str = "Kunal Deshmukh"
    institute: str = "USICT (Information Technology Dept)"
    track: str = "Artificial Intelligence"
    capstone_partner: str = "IBM SkillsBuild & Edunet Foundation"
    repo_url: str = "https://github.com/Kunal77744/AI-Study-Buddy"


PROJECT_METADATA = AppMetadata()


def _clean_secret(value: object) -> str:
    if not isinstance(value, str):
        return ""
    return value.strip().strip('"').strip("'").strip()


def resolve_api_key(override_key: str | None = None) -> str:
    """Resolve Gemini API key from BYOK override, env var, or Streamlit secrets.

    Never logs or returns masked versions; returns stripped key or empty string.
    """
    cleaned_override = _clean_secret(override_key)
    if cleaned_override:
        return cleaned_override

    env_key = _clean_secret(os.getenv("GEMINI_API_KEY", ""))
    if env_key:
        return env_key

    try:
        import streamlit as st

        top_level = _clean_secret(st.secrets.get("GEMINI_API_KEY", ""))
        if top_level:
            return top_level

        for section in st.secrets.values():
            if hasattr(section, "get"):
                nested = _clean_secret(section.get("GEMINI_API_KEY", ""))
                if nested:
                    return nested
    except Exception:
        pass

    return ""
