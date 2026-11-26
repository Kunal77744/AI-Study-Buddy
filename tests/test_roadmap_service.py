"""Unit tests for services.roadmap_service."""

import pytest

from services.roadmap_service import build_roadmap_prompt
from utils.exceptions import ValidationError


def test_build_roadmap_prompt_valid() -> None:
    prompt, sys_inst = build_roadmap_prompt("System Design", "4 Weeks", "Intermediate", 3)
    assert "4 Weeks" in prompt
    assert "System Design" in prompt
    assert "Intermediate" in prompt
    assert "3 hour(s)" in prompt
    assert "study roadmaps" in sys_inst


def test_build_roadmap_prompt_invalid_inputs() -> None:
    with pytest.raises(ValidationError, match="Learning goal"):
        build_roadmap_prompt("   ", "4 Weeks", "Beginner", 2)
    with pytest.raises(ValidationError, match="duration"):
        build_roadmap_prompt("Python", "10 Years", "Beginner", 2)
    with pytest.raises(ValidationError, match="level"):
        build_roadmap_prompt("Python", "2 Weeks", "Expert", 2)
    with pytest.raises(ValidationError, match="hours"):
        build_roadmap_prompt("Python", "2 Weeks", "Beginner", 0)
