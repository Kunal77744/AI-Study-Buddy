"""Study Roadmap prompt construction and validation."""

from config.settings import ROADMAP_DURATIONS, ROADMAP_LEVELS
from utils.exceptions import ValidationError
from utils.validators import validate_non_empty_text


def build_roadmap_prompt(
    goal: str,
    duration: str,
    level: str,
    hours_per_day: int = 2,
) -> tuple[str, str]:
    """Validate inputs and construct (prompt, system_instruction) for a study roadmap."""
    cleaned_goal = validate_non_empty_text(goal, "Learning goal")
    if duration not in ROADMAP_DURATIONS:
        raise ValidationError(f"Unsupported duration '{duration}'.")
    if level not in ROADMAP_LEVELS:
        raise ValidationError(f"Unsupported level '{level}'.")
    if (
        not isinstance(hours_per_day, int)
        or isinstance(hours_per_day, bool)
        or not (1 <= hours_per_day <= 12)
    ):
        raise ValidationError("Daily study hours must be between 1 and 12.")

    prompt = (
        f"Create a structured, practical {duration} study roadmap for: '{cleaned_goal}'.\n"
        f"Student level: {level}\n"
        f"Available study time: {hours_per_day} hour(s) per day\n\n"
        "Format the roadmap in clean Markdown with:\n"
        "1. **Overview & Learning Outcomes**\n"
        "2. **Week-by-Week / Phase Breakdown** (with specific topics and daily/weekly goals)\n"
        "3. **Hands-On Practice & Mini-Projects**\n"
        "4. **Quick Revision & Self-Assessment Checklist**\n"
        "Keep it actionable, realistic, and encouraging."
    )
    system_instruction = (
        "You are an expert academic mentor who designs clear, structured, "
        "step-by-step study roadmaps for students."
    )
    return prompt, system_instruction
