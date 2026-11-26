"""Study Roadmap Generator UI component."""

import re

import streamlit as st

from config.settings import ROADMAP_DURATIONS, ROADMAP_LEVELS
from services.gemini_service import generate_text
from services.roadmap_service import build_roadmap_prompt
from utils.exceptions import (
    ConfigurationError,
    GeminiAPIError,
    GeminiRateLimitError,
    StudyBuddyError,
)


def _safe_filename(goal: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9_-]+", "_", goal.strip()).strip("_")
    return f"Roadmap_{slug[:40] or 'Study'}.md"


def render_roadmap_ui() -> None:
    """Render the Study Roadmap Generator section."""
    st.markdown("### 🗺️ Personalized Study Roadmap")
    st.caption(
        "Turn any subject or skill into a structured, step-by-step study plan "
        "tailored to your schedule and level."
    )

    col1, col2 = st.columns([2, 1])
    with col1:
        goal_input = st.text_input(
            "What do you want to learn?",
            placeholder="e.g. Python for Data Science, System Design, DBMS, Web Development",
        )
    with col2:
        duration = st.selectbox("Target Duration", list(ROADMAP_DURATIONS), index=2)

    col3, col4 = st.columns(2)
    with col3:
        level = st.selectbox("Current Level", list(ROADMAP_LEVELS), index=0)
    with col4:
        hours_per_day = int(
            st.slider("Daily Study Time (hours)", min_value=1, max_value=8, value=2)
        )

    if st.button("🗺️ Generate Study Roadmap", type="primary", use_container_width=True):
        try:
            prompt, sys_inst = build_roadmap_prompt(goal_input, duration, level, hours_per_day)
            with st.spinner(f"Building your {duration} study roadmap..."):
                roadmap_text = generate_text(prompt, system_instruction=sys_inst)
            st.session_state["last_roadmap"] = roadmap_text
            st.session_state["last_roadmap_goal"] = goal_input.strip()
        except ConfigurationError:
            st.error(
                "AI Study Assistant is currently unavailable. "
                "Please try again later."
            )
        except GeminiRateLimitError:
            st.error(
                "Too many requests right now. Please wait a moment and try again."
            )
        except GeminiAPIError:
            st.error(
                "Could not generate your roadmap right now. "
                "Please wait a moment and try again."
            )
        except StudyBuddyError as exc:
            st.error(f"Notice: {exc}")

    if "last_roadmap" in st.session_state:
        st.markdown("---")
        st.markdown("#### 📋 Your Study Roadmap")
        st.markdown(st.session_state["last_roadmap"])
        st.download_button(
            label="📥 Download Roadmap (.md)",
            data=st.session_state["last_roadmap"],
            file_name=_safe_filename(st.session_state.get("last_roadmap_goal", "Study")),
            mime="text/markdown",
        )
