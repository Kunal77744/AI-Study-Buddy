"""AI Study Buddy — Student-Facing Streamlit Application."""

import streamlit as st

from components.quiz_ui import render_quiz_ui
from components.sidebar import NAV_ITEMS, render_sidebar
from components.study_planner import render_study_planner
from components.summarizer import render_summarizer
from components.topic_explainer import render_topic_explainer
from config.settings import APP_ICON

st.set_page_config(
    page_title="AI Study Buddy",
    page_icon=APP_ICON,
    layout="wide",
    initial_sidebar_state="expanded",
)

# Clean, accessible, responsive educational SaaS styling
st.markdown(
    """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        line-height: 1.6;
    }

    .stApp {
        background-color: #F8FAFC;
        overflow-x: hidden;
    }

    /* Accessible keyboard focus indicator */
    button:focus-visible,
    [role="radio"]:focus-visible,
    input:focus-visible,
    textarea:focus-visible,
    select:focus-visible {
        outline: 2px solid #2563EB !important;
        outline-offset: 2px !important;
    }

    .hero-banner {
        background: linear-gradient(135deg, #0F172A 0%, #1E293B 55%, #2563EB 100%);
        padding: 2rem 1.8rem;
        border-radius: 16px;
        color: #FFFFFF;
        margin-bottom: 1.5rem;
        box-shadow: 0 10px 20px -8px rgba(15, 23, 42, 0.2);
    }

    .hero-banner h1 {
        font-size: 2rem;
        font-weight: 700;
        color: #FFFFFF !important;
        margin-bottom: 0.5rem;
        letter-spacing: -0.02em;
    }

    .hero-banner p {
        font-size: 1rem;
        color: #E2E8F0;
        max-width: 760px;
        margin-bottom: 0;
        line-height: 1.6;
    }

    .feature-card {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 14px;
        padding: 1.25rem 1.1rem;
        height: 100%;
        box-shadow: 0 2px 6px rgba(15, 23, 42, 0.04);
        margin-bottom: 0.6rem;
    }

    .feature-card-active {
        border: 1.5px solid #2563EB;
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.12);
    }

    .feature-card-icon {
        font-size: 1.5rem;
        margin-bottom: 0.4rem;
    }

    .feature-card h3 {
        font-size: 1.05rem;
        font-weight: 700;
        color: #0F172A;
        margin: 0 0 0.35rem 0;
    }

    .feature-card p {
        font-size: 0.9rem;
        color: #475569;
        margin: 0;
        line-height: 1.5;
    }

    section[data-testid="stSidebar"] {
        background-color: #FFFFFF;
        border-right: 1px solid #E2E8F0;
    }

    .sidebar-header {
        display: flex;
        align-items: center;
        gap: 12px;
        padding-bottom: 0.8rem;
        border-bottom: 1px solid #F1F5F9;
        margin-bottom: 1rem;
    }

    .sidebar-header h2 {
        font-size: 1.15rem;
        font-weight: 700;
        color: #0F172A;
        margin: 0;
    }

    .sidebar-tagline {
        font-size: 0.78rem;
        color: #475569;
    }

    .quiz-score-card {
        background: #047857;
        color: #FFFFFF;
        padding: 1.5rem;
        border-radius: 14px;
        text-align: center;
        margin-bottom: 1.4rem;
    }

    .quiz-score-warning {
        background: #B45309;
        color: #FFFFFF;
        padding: 1.5rem;
        border-radius: 14px;
        text-align: center;
        margin-bottom: 1.4rem;
    }

    .stButton > button {
        border-radius: 8px;
        font-weight: 600;
    }

    @media (max-width: 768px) {
        .hero-banner {
            padding: 1.4rem 1.2rem;
            border-radius: 12px;
        }
        .hero-banner h1 {
            font-size: 1.5rem;
        }
        .hero-banner p {
            font-size: 0.95rem;
        }
    }
</style>
""",
    unsafe_allow_html=True,
)


def _select_section(section_label: str) -> None:
    st.session_state.active_section = section_label


active_section = render_sidebar()

st.markdown(
    """
<div class="hero-banner">
    <h1>Learn Smarter. Study Better.</h1>
    <p>Your personal AI-powered learning companion for understanding concepts,
    creating notes, practising quizzes and staying focused.</p>
</div>
""",
    unsafe_allow_html=True,
)

FEATURE_CARDS = [
    (
        "💡",
        "Topic Explainer",
        "Understand difficult topics through simple explanations and examples.",
        NAV_ITEMS[0],
        "Open Explainer",
    ),
    (
        "📝",
        "Smart Summarizer",
        "Convert PDFs and text into structured study notes.",
        NAV_ITEMS[1],
        "Open Summarizer",
    ),
    (
        "🧠",
        "Interactive Quiz",
        "Generate MCQs and test your understanding.",
        NAV_ITEMS[2],
        "Open Quiz",
    ),
    (
        "⏱️",
        "Focus Planner",
        "Organize study sessions using a Pomodoro timer.",
        NAV_ITEMS[3],
        "Open Planner",
    ),
]

card_cols = st.columns(4)
for col, (icon, title, desc, target, btn_label) in zip(card_cols, FEATURE_CARDS, strict=True):
    with col:
        active_cls = " feature-card-active" if active_section == target else ""
        st.markdown(
            f"""
            <div class="feature-card{active_cls}">
                <div class="feature-card-icon" aria-hidden="true">{icon}</div>
                <h3>{title}</h3>
                <p>{desc}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.button(
            btn_label,
            key=f"card_btn_{title}",
            on_click=_select_section,
            args=(target,),
            type="primary" if active_section == target else "secondary",
            use_container_width=True,
        )

st.markdown("---")

if active_section == NAV_ITEMS[0]:
    render_topic_explainer()
elif active_section == NAV_ITEMS[1]:
    render_summarizer()
elif active_section == NAV_ITEMS[2]:
    render_quiz_ui()
elif active_section == NAV_ITEMS[3]:
    render_study_planner()

st.divider()
st.caption("AI Study Buddy | Your Learning Companion")
