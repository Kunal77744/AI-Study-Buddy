"""Tab 5 UI: Architecture & Capstone Submission Details."""

import streamlit as st

from config.settings import PROJECT_METADATA


def render_architecture_tab() -> None:
    """Render the Architecture & Documentation tab."""
    st.markdown("### ℹ️ Architecture & Capstone Submission Details")

    st.markdown(
        f"""
        #### 🎯 Problem Statement & Key Challenges
        Students face significant hurdles during self-study:
        - Academic concepts can be complex and difficult to grasp without on-demand tutoring.
        - Standard search engines yield lengthy, unstructured, or noisy results.
        - Mentors and teachers are not available round-the-clock for instant doubt resolution.
        - Lack of unified, interactive tools for instant note summarization and self-assessment.

        ---

        #### 💡 Solution & Core Modules
        **{PROJECT_METADATA.title}** is a modular Streamlit web application powered by
        **Google Gemini** (`gemini-2.5-flash`, `gemini-1.5-flash`, `gemini-1.5-pro`):
        - **Topic Explainer (`components/topic_explainer.py`):** Simplifies complex theories
          with level-tailored analogies and Markdown exports.
        - **Document Summarizer (`components/summarizer.py`, `services/pdf_service.py`):**
          Validates and extracts text from PDF/text files with caching and size/page limits.
        - **Interactive MCQ Engine (`components/quiz_ui.py`, `services/quiz_service.py`):**
          Validates quiz JSON schemas, scores answers, and provides detailed explanations.
        - **Productivity Suite (`components/study_planner.py`, `services/timer_service.py`):**
          Non-blocking timestamp-based Pomodoro timer (Start, Pause, Resume, Reset) and checklist.

        ---

        #### 🏗️ System Workflow Architecture
        ```text
        Streamlit UI (components/)
            │
            ▼
        Validation & Services (utils/, services/)
            ├── pdf_service.py    ──► pypdf (cached text extraction)
            ├── quiz_service.py   ──► JSON parsing + schema validation
            ├── timer_service.py  ──► Non-blocking monotonic timestamp state
            └── gemini_service.py ──► Google Gemini API (explicit model, retries, timeout)
        ```

        ---

        #### 👨‍🎓 Project Credits & Submission Info
        - **Developer:** {PROJECT_METADATA.author}
        - **Institute:** {PROJECT_METADATA.institute}
        - **Track:** {PROJECT_METADATA.track}
        - **Capstone Partner:** {PROJECT_METADATA.capstone_partner}
        - **GitHub Repo:** [{PROJECT_METADATA.repo_url}]({PROJECT_METADATA.repo_url})
        """
    )
