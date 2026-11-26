"""Non-blocking, timestamp-based Pomodoro timer state logic."""

import time
from dataclasses import dataclass


@dataclass
class PomodoroState:
    """Represents the state of a Pomodoro countdown timer."""

    duration_seconds: int
    status: str = "idle"  # "idle" | "running" | "paused" | "completed"
    end_timestamp: float | None = None
    remaining_seconds: int = 0

    def __post_init__(self) -> None:
        if self.status == "idle" and self.remaining_seconds == 0:
            self.remaining_seconds = self.duration_seconds


def start_timer(duration_minutes: int, now: float | None = None) -> PomodoroState:
    """Start a new countdown session from the given duration in minutes."""
    current = time.monotonic() if now is None else now
    total_sec = max(1, duration_minutes * 60)
    return PomodoroState(
        duration_seconds=total_sec,
        status="running",
        end_timestamp=current + total_sec,
        remaining_seconds=total_sec,
    )


def pause_timer(state: PomodoroState, now: float | None = None) -> PomodoroState:
    """Pause a running timer, freezing its remaining seconds."""
    if state.status != "running":
        return state
    remaining = get_remaining_seconds(state, now=now)
    if remaining <= 0:
        return PomodoroState(
            duration_seconds=state.duration_seconds,
            status="completed",
            end_timestamp=None,
            remaining_seconds=0,
        )
    return PomodoroState(
        duration_seconds=state.duration_seconds,
        status="paused",
        end_timestamp=None,
        remaining_seconds=remaining,
    )


def resume_timer(state: PomodoroState, now: float | None = None) -> PomodoroState:
    """Resume a paused timer from its frozen remaining seconds."""
    if state.status != "paused" or state.remaining_seconds <= 0:
        return state
    current = time.monotonic() if now is None else now
    return PomodoroState(
        duration_seconds=state.duration_seconds,
        status="running",
        end_timestamp=current + state.remaining_seconds,
        remaining_seconds=state.remaining_seconds,
    )


def reset_timer(duration_minutes: int) -> PomodoroState:
    """Reset the timer back to idle with the selected preset duration."""
    total_sec = max(1, duration_minutes * 60)
    return PomodoroState(
        duration_seconds=total_sec,
        status="idle",
        end_timestamp=None,
        remaining_seconds=total_sec,
    )


def get_remaining_seconds(state: PomodoroState, now: float | None = None) -> int:
    """Compute remaining seconds without blocking."""
    if state.status == "running" and state.end_timestamp is not None:
        current = time.monotonic() if now is None else now
        remaining = int(round(state.end_timestamp - current))
        return max(0, remaining)
    if state.status == "completed":
        return 0
    return max(0, state.remaining_seconds)


def sync_timer_state(state: PomodoroState, now: float | None = None) -> PomodoroState:
    """Update state to 'completed' if a running timer has reached zero."""
    if state.status != "running":
        return state
    remaining = get_remaining_seconds(state, now=now)
    if remaining <= 0:
        return PomodoroState(
            duration_seconds=state.duration_seconds,
            status="completed",
            end_timestamp=None,
            remaining_seconds=0,
        )
    return state


def format_mm_ss(total_seconds: int) -> str:
    """Format seconds as MM:SS."""
    minutes, seconds = divmod(max(0, total_seconds), 60)
    return f"{minutes:02d}:{seconds:02d}"
