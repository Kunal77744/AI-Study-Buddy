"""Smoke, navigation, and state-isolation tests for the student-facing Streamlit app."""

from unittest.mock import patch

from streamlit.testing.v1 import AppTest

from components.sidebar import NAV_ITEMS


def test_app_renders_four_sections_without_developer_controls() -> None:
    """Verify app.py renders cleanly with 4 nav items and no developer-only UI controls."""
    at = AppTest.from_file("app.py", default_timeout=15)
    at.run()
    assert not at.exception

    # Verify 4 navigation items in sidebar
    nav_radios = [r for r in at.radio if r.key == "active_section"]
    assert len(nav_radios) == 1
    assert tuple(nav_radios[0].options) == NAV_ITEMS

    # Verify developer controls are absent from student-facing UI
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


def test_consecutive_quizzes_do_not_carry_over_answers() -> None:
    """Verify navigating to Quiz and generating consecutive quizzes resets radio selections."""
    quiz_1 = '[{"id":1,"question":"Q1?","options":["A1","B1"],"answer":"A1","explanation":"E1"}]'
    quiz_2 = '[{"id":1,"question":"Q2?","options":["A2","B2"],"answer":"B2","explanation":"E2"}]'

    with patch("components.quiz_ui.generate_text", side_effect=[quiz_1, quiz_2]):
        at = AppTest.from_file("app.py", default_timeout=15)
        at.run()

        # Navigate to Quiz using the dashboard feature card button
        quiz_card_btn = [b for b in at.button if b.label == "Open Quiz"][0]
        quiz_card_btn.click().run()
        assert at.session_state["active_section"] == NAV_ITEMS[2]

        quiz_topic_input = [
            ti for ti in at.text_input if "Operating Systems" in (ti.placeholder or "")
        ][0]
        quiz_topic_input.set_value("OS").run()

        gen_btn = [b for b in at.button if "Generate Custom Quiz" in b.label][0]
        gen_btn.click().run()
        assert not at.exception
        assert at.session_state["quiz_generation_id"] == 1

        radio_q1 = [r for r in at.radio if r.key == "quiz_1_opt_0"][0]
        radio_q1.set_value("A1").run()

        gen_btn = [b for b in at.button if "Generate Custom Quiz" in b.label][0]
        gen_btn.click().run()
        assert not at.exception
        assert at.session_state["quiz_generation_id"] == 2
        radio_q2 = [r for r in at.radio if r.key == "quiz_2_opt_0"][0]
        assert radio_q2.value is None
