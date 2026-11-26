"""Product navigation sidebar for AI Study Buddy."""

import streamlit as st

from config.settings import resolve_api_key

NAV_ITEMS: tuple[str, ...] = (
    "💡 Explainer",
    "📝 Summarizer",
    "🧠 Quiz",
    "⏱️ Planner",
)


def render_sidebar() -> str:
    """Render the student-facing navigation sidebar and return the active section."""
    if "active_section" not in st.session_state:
        st.session_state.active_section = NAV_ITEMS[0]

    with st.sidebar:
        st.markdown(
            """
            <div class="sidebar-header">
                <span style="font-size: 28px;" aria-hidden="true">🎓</span>
                <div>
                    <h2>AI Study Buddy</h2>
                    <span class="sidebar-tagline">Your Personal Learning Companion</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("##### Study Tools")
        selected = st.radio(
            "Navigate to a study tool",
            options=list(NAV_ITEMS),
            key="active_section",
            label_visibility="collapsed",
        )

        st.divider()

        is_ready = bool(resolve_api_key())
        if is_ready:
            st.caption("🟢 Study Assistant: Ready")
        else:
            st.caption("🟡 Study Assistant: Unavailable")

    return selected
