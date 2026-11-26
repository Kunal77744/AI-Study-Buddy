"""Interactive MCQ Quiz Generator UI component."""

import streamlit as st

from config.settings import (
    DEFAULT_QUIZ_QUESTIONS,
    MAX_QUIZ_QUESTIONS,
    MIN_QUIZ_QUESTIONS,
    QUIZ_DIFFICULTIES,
)
from services.gemini_service import generate_text
from services.quiz_service import (
    QuizQuestion,
    build_quiz_prompt,
    evaluate_quiz,
    parse_and_validate_quiz,
)
from utils.exceptions import (
    ConfigurationError,
    GeminiAPIError,
    GeminiRateLimitError,
    QuizParseError,
    StudyBuddyError,
)


def render_quiz_ui() -> None:
    """Render the Interactive MCQ Quiz Generator section."""
    st.markdown("### 🧠 Interactive MCQ Quiz Generator")
    st.caption(
        "Generate practice quizzes, test your knowledge, and review scorecards "
        "with detailed explanations."
    )

    if "quiz_data" not in st.session_state:
        st.session_state.quiz_data = None
    if "quiz_submitted" not in st.session_state:
        st.session_state.quiz_submitted = False
    if "quiz_generation_id" not in st.session_state:
        st.session_state.quiz_generation_id = 0

    col_q1, col_q2, col_q3 = st.columns([2, 1, 1])
    with col_q1:
        quiz_subject = st.text_input(
            "Quiz Topic / Subject",
            placeholder="e.g. Operating Systems, Data Structures, Machine Learning",
        )
    with col_q2:
        num_q = int(
            st.number_input(
                "Questions Count",
                min_value=MIN_QUIZ_QUESTIONS,
                max_value=MAX_QUIZ_QUESTIONS,
                value=DEFAULT_QUIZ_QUESTIONS,
            )
        )
    with col_q3:
        difficulty = st.selectbox("Difficulty Level", list(QUIZ_DIFFICULTIES))

    if st.button("🎯 Generate Custom Quiz", type="primary"):
        try:
            prompt, sys_inst = build_quiz_prompt(quiz_subject, num_q, difficulty)
            with st.spinner(f"Generating {num_q} {difficulty} questions on '{quiz_subject}'..."):
                raw_res = generate_text(
                    prompt,
                    system_instruction=sys_inst,
                )
            quiz_list = parse_and_validate_quiz(raw_res)
            st.session_state.quiz_data = quiz_list
            st.session_state.quiz_submitted = False
            st.session_state.quiz_generation_id += 1
            st.success(
                f"Generated {len(quiz_list)} question(s) on '{quiz_subject.strip()}'."
            )
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
                "Could not generate the quiz right now. "
                "Please wait a moment and try again."
            )
        except QuizParseError:
            st.error(
                "The generated quiz could not be formatted properly. "
                "Please try generating again."
            )
        except StudyBuddyError as exc:
            st.error(f"Notice: {exc}")

    questions: list[QuizQuestion] | None = st.session_state.quiz_data
    gen_id: int = st.session_state.quiz_generation_id

    if questions:
        st.markdown("---")
        st.markdown("#### 📝 Select Your Answers:")

        with st.form(key=f"interactive_quiz_form_{gen_id}"):
            for idx, item in enumerate(questions):
                st.markdown(f"**Q{idx + 1}. {item.question}**")
                st.radio(
                    f"Options for Q{idx + 1}:",
                    options=list(item.options),
                    key=f"quiz_{gen_id}_opt_{idx}",
                    index=None,
                )
                st.markdown("")

            submit_quiz = st.form_submit_button(
                "🏆 Submit Quiz Answers", type="primary", use_container_width=True
            )
            if submit_quiz:
                st.session_state.quiz_submitted = True
    else:
        st.info("Enter a topic above and click **Generate Custom Quiz** to begin.")

    if st.session_state.get("quiz_submitted", False) and questions:
        user_answers = {
            idx: st.session_state.get(f"quiz_{gen_id}_opt_{idx}")
            for idx in range(len(questions))
        }
        evaluation = evaluate_quiz(questions, user_answers)
        card_class = "quiz-score-card" if evaluation.passed else "quiz-score-warning"
        feedback = (
            "🎉 Outstanding! You have mastered this concept."
            if evaluation.passed
            else "👍 Good effort! Review the explanations below to strengthen your understanding."
        )

        st.markdown(
            f"""
            <div class="{card_class}">
                <h2 style="margin:0; font-size: 2rem;">
                    Quiz Scorecard: {evaluation.score} / {evaluation.total}
                    ({evaluation.percentage}%)
                </h2>
                <p style="margin-top: 0.4rem; font-size: 1.1rem; opacity: 0.95;">
                    {feedback}
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.progress(evaluation.percentage / 100.0)

        st.markdown("#### 🔍 Answer Key & Detailed Explanations:")
        for res in evaluation.results:
            exp_label = (
                f"Question {res.question_number}: "
                f"{'✅ Correct' if res.is_correct else '❌ Incorrect'}"
            )
            with st.expander(exp_label, expanded=True):
                st.markdown(f"**Question:** {res.question}")
                st.markdown(f"**Your Answer:** `{res.user_answer or 'Not Answered'}`")
                st.markdown(f"**Correct Option:** `{res.correct_answer}`")
                st.info(f"**Explanation:** {res.explanation}")
