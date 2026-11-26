"""Topic Explainer UI component."""

import re

import streamlit as st

from services.gemini_service import stream_text
from utils.exceptions import (
    ConfigurationError,
    GeminiAPIError,
    GeminiRateLimitError,
    StudyBuddyError,
)
from utils.validators import validate_non_empty_text


def _safe_filename(topic: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9_-]+", "_", topic.strip()).strip("_")
    return f"Explanation_{slug[:40] or 'Topic'}.md"


def render_topic_explainer() -> None:
    """Render the Topic Explainer section."""
    st.markdown("### 💡 Explain Any Academic Concept")
    st.caption(
        "Master complex subjects with intuitive explanations, real-world analogies, "
        "and step-by-step breakdowns."
    )

    col1, col2 = st.columns([2, 1])
    with col1:
        topic_input = st.text_input(
            "Enter Topic or Question to Explore",
            placeholder=(
                "e.g. Backpropagation in Neural Networks, Quantum Entanglement, "
                "Normalization in DBMS, TCP/IP Model"
            ),
        )
    with col2:
        explanation_level = st.selectbox(
            "Target Audience Level",
            [
                "ELI5 (Explain Like I'm Five)",
                "High School Student",
                "Undergraduate / Technical",
                "Analogy-First Approach",
            ],
            index=0,
        )

    learning_options = st.multiselect(
        "Customize Explanation Features:",
        [
            "Analogies",
            "Step-by-Step",
            "Formulas & Code",
            "Self-Check",
        ],
        default=[
            "Analogies",
            "Step-by-Step",
            "Self-Check",
        ],
    )

    just_streamed = False
    if st.button("🚀 Explain Concept", type="primary", use_container_width=True):
        try:
            cleaned_topic = validate_non_empty_text(topic_input, "Topic")
            features = ", ".join(learning_options) if learning_options else "Clear Overview"
            prompt = (
                f"Explain the topic: '{cleaned_topic}' for target audience level: "
                f"'{explanation_level}'.\n"
                f"Include the following components in structured markdown format: {features}.\n"
                "Ensure clean formatting with headings, bullet points, and bold text."
            )
            system_prompt = (
                "You are an elite, encouraging AI Professor dedicated to making "
                "complex ideas crystal clear."
            )
            st.markdown("---")
            st.markdown("#### 📖 Explanation Output")
            response_text = str(
                st.write_stream(stream_text(prompt, system_instruction=system_prompt))
            )
            st.session_state["last_explanation"] = response_text
            st.session_state["last_topic"] = cleaned_topic
            just_streamed = True
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
                "Could not generate an explanation right now. "
                "Please wait a moment and try again."
            )
        except StudyBuddyError as exc:
            st.error(f"Notice: {exc}")

    if "last_explanation" in st.session_state:
        if not just_streamed:
            st.markdown("---")
            st.markdown("#### 📖 Explanation Output")
            st.markdown(st.session_state["last_explanation"])
        st.download_button(
            label="📥 Download Explanation (.md)",
            data=st.session_state["last_explanation"],
            file_name=_safe_filename(st.session_state.get("last_topic", "Topic")),
            mime="text/markdown",
        )
