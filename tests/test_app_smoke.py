"""Integration-style AppTest tests for all four student-facing sections."""

from unittest.mock import patch

from streamlit.testing.v1 import AppTest

from components.sidebar import NAV_ITEMS
from utils.exceptions import ConfigurationError, GeminiAuthError, GeminiRateLimitError


def test_app_renders_four_sections_without_developer_controls() -> None:
    """Verify app.py renders cleanly with 4 nav items and no developer-only UI controls."""
    at = AppTest.from_file("app.py", default_timeout=15)
    at.run()
    assert not at.exception

    nav_radios = [r for r in at.radio if r.key == "active_section"]
    assert len(nav_radios) == 1
    assert tuple(nav_radios[0].options) == NAV_ITEMS

    assert not at.selectbox or all("Model" not in (s.label or "") for s in at.selectbox)
    assert all("API Key" not in (ti.label or "") for ti in at.text_input)
    assert all("Developer Settings" not in (e.label or "") for e in at.expander)


def test_all_four_navigation_sections_render_cleanly() -> None:
    """Verify switching between Explainer, Summarizer, Quiz, and Planner works without errors."""
    at = AppTest.from_file("app.py", default_timeout=15)
    at.run()

    for nav_label in NAV_ITEMS:
        nav_radio = [r for r in at.radio if r.key == "active_section"][0]
        nav_radio.set_value(nav_label).run()
        assert not at.exception


def test_topic_explainer_success_and_error_states() -> None:
    """Verify Topic Explainer renders AI output on success and friendly errors on failure."""
    with patch("components.topic_explainer.generate_text", return_value="## Simple Binary Trees"):
        at = AppTest.from_file("app.py", default_timeout=15)
        at.run()

        topic_input = [
            ti for ti in at.text_input if "Backpropagation" in (ti.placeholder or "")
        ][0]
        topic_input.set_value("Binary Trees").run()
        explain_btn = [b for b in at.button if "Explain Concept" in b.label][0]
        explain_btn.click().run()

        assert not at.exception
        assert at.session_state["last_explanation"] == "## Simple Binary Trees"

    with patch(
        "components.topic_explainer.generate_text",
        side_effect=GeminiRateLimitError("429"),
    ):
        at = AppTest.from_file("app.py", default_timeout=15)
        at.run()
        topic_input = [
            ti for ti in at.text_input if "Backpropagation" in (ti.placeholder or "")
        ][0]
        topic_input.set_value("Binary Trees").run()
        explain_btn = [b for b in at.button if "Explain Concept" in b.label][0]
        explain_btn.click().run()
        assert any("Too many requests" in e.value for e in at.error)

    with patch(
        "components.topic_explainer.generate_text",
        side_effect=ConfigurationError("missing"),
    ):
        at = AppTest.from_file("app.py", default_timeout=15)
        at.run()
        topic_input = [
            ti for ti in at.text_input if "Backpropagation" in (ti.placeholder or "")
        ][0]
        topic_input.set_value("Binary Trees").run()
        explain_btn = [b for b in at.button if "Explain Concept" in b.label][0]
        explain_btn.click().run()
        assert any("currently unavailable" in e.value for e in at.error)


def test_summarizer_text_flow_and_auth_error() -> None:
    """Verify Summarizer handles pasted notes and friendly auth error states."""
    with patch("components.summarizer.generate_text", return_value="- Key point 1"):
        at = AppTest.from_file("app.py", default_timeout=15)
        at.run()
        [b for b in at.button if b.label == "Open Summarizer"][0].click().run()

        at.text_area[0].set_value("Lecture notes about operating systems.").run()
        [b for b in at.button if "Summarize Document" in b.label][0].click().run()
        assert not at.exception
        assert at.session_state["last_summary"] == "- Key point 1"

    with patch(
        "components.summarizer.generate_text",
        side_effect=GeminiAuthError("invalid"),
    ):
        at = AppTest.from_file("app.py", default_timeout=15)
        at.run()
        [b for b in at.button if b.label == "Open Summarizer"][0].click().run()
        at.text_area[0].set_value("Lecture notes.").run()
        [b for b in at.button if "Summarize Document" in b.label][0].click().run()
        assert any("Could not generate a summary" in e.value for e in at.error)


def test_roadmap_flow_and_error_state() -> None:
    """Verify Study Roadmap renders output on success and friendly errors on failure."""
    with patch("components.roadmap_ui.generate_text", return_value="## Week 1: Basics"):
        at = AppTest.from_file("app.py", default_timeout=15)
        at.run()
        [b for b in at.button if b.label == "Open Roadmap"][0].click().run()
        assert at.session_state["active_section"] == NAV_ITEMS[3]

        goal_input = [
            ti for ti in at.text_input if "Data Science" in (ti.placeholder or "")
        ][0]
        goal_input.set_value("Python").run()
        [b for b in at.button if "Generate Study Roadmap" in b.label][0].click().run()
        assert not at.exception
        assert at.session_state["last_roadmap"] == "## Week 1: Basics"

    with patch(
        "components.roadmap_ui.generate_text",
        side_effect=GeminiRateLimitError("429"),
    ):
        at = AppTest.from_file("app.py", default_timeout=15)
        at.run()
        [b for b in at.button if b.label == "Open Roadmap"][0].click().run()
        goal_input = [
            ti for ti in at.text_input if "Data Science" in (ti.placeholder or "")
        ][0]
        goal_input.set_value("Python").run()
        [b for b in at.button if "Generate Study Roadmap" in b.label][0].click().run()
        assert any("Too many requests" in e.value for e in at.error)


def test_consecutive_quizzes_do_not_carry_over_answers() -> None:
    """Verify navigating to Quiz and generating consecutive quizzes resets radio selections."""
    quiz_1 = '[{"id":1,"question":"Q1?","options":["A1","B1"],"answer":"A1","explanation":"E1"}]'
    quiz_2 = '[{"id":1,"question":"Q2?","options":["A2","B2"],"answer":"B2","explanation":"E2"}]'

    with patch("components.quiz_ui.generate_text", side_effect=[quiz_1, quiz_2]):
        at = AppTest.from_file("app.py", default_timeout=15)
        at.run()

        [b for b in at.button if b.label == "Open Quiz"][0].click().run()
        assert at.session_state["active_section"] == NAV_ITEMS[2]

        quiz_topic_input = [
            ti for ti in at.text_input if "Operating Systems" in (ti.placeholder or "")
        ][0]
        quiz_topic_input.set_value("OS").run()

        [b for b in at.button if "Generate Custom Quiz" in b.label][0].click().run()
        assert not at.exception
        assert at.session_state["quiz_generation_id"] == 1

        radio_q1 = [r for r in at.radio if r.key == "quiz_1_opt_0"][0]
        radio_q1.set_value("A1").run()

        [b for b in at.button if "Generate Custom Quiz" in b.label][0].click().run()
        assert not at.exception
        assert at.session_state["quiz_generation_id"] == 2
        radio_q2 = [r for r in at.radio if r.key == "quiz_2_opt_0"][0]
        assert radio_q2.value is None
