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
    "gemini-2.5-flash (Recommended)": "gemini-2.5-flash",
    "gemini-1.5-flash": "gemini-1.5-flash",
    "gemini-1.5-pro": "gemini-1.5-pro",
}
DEFAULT_MODEL_LABEL = "gemini-2.5-flash (Recommended)"
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

# Pomodoro timer presets (label -> minutes)
TIMER_PRESETS: dict[str, int] = {
    "25 min (Focus)": 25,
    "5 min (Short Break)": 5,
    "15 min (Long Break)": 15,
}
DEFAULT_TIMER_PRESET = "25 min (Focus)"


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


def resolve_api_key(override_key: str | None = None) -> str:
    """Resolve Gemini API key from BYOK override, env var, or Streamlit secrets.

    Never logs or returns masked versions; returns stripped key or empty string.
    """
    if override_key and override_key.strip():
        return override_key.strip()

    env_key = os.getenv("GEMINI_API_KEY", "").strip()
    if env_key:
        return env_key

    try:
        import streamlit as st

        secret_key = str(st.secrets.get("GEMINI_API_KEY", "")).strip()
        if secret_key:
            return secret_key
    except Exception:
        pass

    return ""
