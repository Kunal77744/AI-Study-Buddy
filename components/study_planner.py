"""Tab 4 UI: Non-blocking Pomodoro Focus Timer & Daily Study Goals Checklist."""

import streamlit as st

from config.settings import DEFAULT_TIMER_PRESET, TIMER_PRESETS
from services.timer_service import (
    PomodoroState,
    format_mm_ss,
    get_remaining_seconds,
    pause_timer,
    reset_timer,
    resume_timer,
    start_timer,
    sync_timer_state,
)


def _render_timer_panel() -> None:
    """Render the Pomodoro timer with a non-blocking fragment when running."""
    st.markdown("#### ⌛ Pomodoro Focus Session")
    preset = st.radio(
        "Select Timer Preset:",
        list(TIMER_PRESETS.keys()),
        index=list(TIMER_PRESETS.keys()).index(DEFAULT_TIMER_PRESET),
        horizontal=True,
    )
    session_mins = TIMER_PRESETS[preset]

    if "pomodoro_state" not in st.session_state:
        st.session_state.pomodoro_state = reset_timer(session_mins)
    elif (
        st.session_state.pomodoro_state.status == "idle"
        and st.session_state.pomodoro_state.duration_seconds != session_mins * 60
    ):
        st.session_state.pomodoro_state = reset_timer(session_mins)

    state: PomodoroState = sync_timer_state(st.session_state.pomodoro_state)
    st.session_state.pomodoro_state = state

    c1, c2, c3 = st.columns(3)
    with c1:
        if state.status in ("idle", "completed"):
            if st.button("▶️ Start", type="primary", use_container_width=True):
                st.session_state.pomodoro_state = start_timer(session_mins)
                st.rerun()
        elif state.status == "paused":
            if st.button("▶️ Resume", type="primary", use_container_width=True):
                st.session_state.pomodoro_state = resume_timer(state)
                st.rerun()
        else:
            st.button("▶️ Running", disabled=True, use_container_width=True)

    with c2:
        if st.button(
            "⏸️ Pause",
            disabled=(state.status != "running"),
            use_container_width=True,
        ):
            st.session_state.pomodoro_state = pause_timer(state)
            st.rerun()

    with c3:
        if st.button("⏹️ Reset", use_container_width=True):
            st.session_state.pomodoro_state = reset_timer(session_mins)
            st.rerun()

    run_every = 1 if st.session_state.pomodoro_state.status == "running" else None

    @st.fragment(run_every=run_every)
    def _countdown_display() -> None:
        current_state = sync_timer_state(st.session_state.pomodoro_state)
        st.session_state.pomodoro_state = current_state
        remaining = get_remaining_seconds(current_state)
        formatted = format_mm_ss(remaining)

        if current_state.status == "running":
            st.markdown(f"### 🕒 Time Remaining: `{formatted}`")
            progress = 1.0 - (remaining / max(1, current_state.duration_seconds))
            st.progress(min(1.0, max(0.0, progress)))
        elif current_state.status == "paused":
            st.markdown(f"### ⏸️ Paused: `{formatted}`")
        elif current_state.status == "completed":
            st.markdown("### ✅ Completed: `00:00`")
            st.success("🎉 Focus session completed! Take a well-deserved break.")
        else:
            st.markdown(f"### 🕒 Status: Ready (`{formatted}`)")

    _countdown_display()


def _render_goals_checklist() -> None:
    """Render the interactive daily study goals checklist."""
    st.markdown("#### 📌 Daily Study Goals Checklist")
    new_goal = st.text_input(
        "Add a study task:",
        placeholder="e.g. Solve 5 DBMS MCQs, Read Neural Network notes",
    )
    if "goal_list" not in st.session_state:
        st.session_state.goal_list = [
            {"text": "Review AI Study Buddy Capstone Documentation", "done": True},
            {"text": "Complete 25-minute Pomodoro focus block", "done": False},
        ]

    col_g1, col_g2 = st.columns([3, 1])
    with col_g1:
        if st.button("➕ Add Task") and new_goal.strip():
            st.session_state.goal_list.append({"text": new_goal.strip(), "done": False})
            st.rerun()
    with col_g2:
        if st.button("🗑️ Clear Done"):
            st.session_state.goal_list = [
                g for g in st.session_state.goal_list if not g["done"]
            ]
            st.rerun()

    st.markdown("---")
    if not st.session_state.goal_list:
        st.info("No study tasks yet. Add your first goal above!")
        return

    for idx, item in enumerate(st.session_state.goal_list):
        is_done = st.checkbox(item["text"], value=item["done"], key=f"goal_item_{idx}")
        st.session_state.goal_list[idx]["done"] = is_done


def render_study_planner() -> None:
    """Render the Study Planner & Pomodoro Timer tab."""
    st.markdown("### ⏱️ Pomodoro Focus Timer & Task Planner")
    st.caption(
        "Boost study retention with structured non-blocking focus sessions and "
        "daily study goal checklists."
    )

    col_tm1, col_tm2 = st.columns(2)
    with col_tm1:
        _render_timer_panel()
    with col_tm2:
        _render_goals_checklist()
