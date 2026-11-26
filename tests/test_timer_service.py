"""Unit tests for services.timer_service."""

from services.timer_service import (
    format_mm_ss,
    get_remaining_seconds,
    pause_timer,
    reset_timer,
    resume_timer,
    start_timer,
    sync_timer_state,
)


def test_timer_lifecycle_start_pause_resume_complete() -> None:
    state = start_timer(25, now=100.0)
    assert state.status == "running"
    assert get_remaining_seconds(state, now=160.0) == 24 * 60

    paused = pause_timer(state, now=160.0)
    assert paused.status == "paused"
    assert get_remaining_seconds(paused, now=500.0) == 24 * 60

    resumed = resume_timer(paused, now=500.0)
    assert resumed.status == "running"
    assert get_remaining_seconds(resumed, now=560.0) == 23 * 60

    completed = sync_timer_state(resumed, now=500.0 + 25 * 60)
    assert completed.status == "completed"
    assert get_remaining_seconds(completed) == 0


def test_reset_timer_returns_idle() -> None:
    state = reset_timer(5)
    assert state.status == "idle"
    assert state.remaining_seconds == 300
    assert format_mm_ss(state.remaining_seconds) == "05:00"


def test_repeated_pause_and_resume_are_idempotent() -> None:
    idle = reset_timer(10)
    assert pause_timer(idle, now=10.0) == idle
    assert resume_timer(idle, now=10.0) == idle

    running = start_timer(10, now=10.0)
    assert resume_timer(running, now=20.0) == running

    paused = pause_timer(running, now=20.0)
    assert pause_timer(paused, now=30.0) == paused


def test_pause_after_expiry_completes_cleanly() -> None:
    running = start_timer(1, now=0.0)
    assert get_remaining_seconds(running, now=120.0) == 0
    finished = pause_timer(running, now=120.0)
    assert finished.status == "completed"
    assert finished.remaining_seconds == 0
