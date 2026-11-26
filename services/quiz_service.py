"""Quiz prompt construction, JSON parsing, schema validation, and scoring."""

import json
from dataclasses import dataclass

from config.settings import QUIZ_DIFFICULTIES, QUIZ_PASS_THRESHOLD_PCT
from utils.exceptions import QuizParseError, ValidationError
from utils.validators import validate_non_empty_text, validate_question_count


@dataclass(frozen=True)
class QuizQuestion:
    """Validated multiple-choice question."""

    id: int
    question: str
    options: tuple[str, ...]
    answer: str
    explanation: str


@dataclass(frozen=True)
class QuestionResult:
    """Evaluation result for a single quiz question."""

    question_number: int
    question: str
    user_answer: str | None
    correct_answer: str
    is_correct: bool
    explanation: str


@dataclass(frozen=True)
class QuizEvaluation:
    """Overall quiz scorecard and per-question breakdown."""

    score: int
    total: int
    percentage: int
    passed: bool
    results: tuple[QuestionResult, ...]


def build_quiz_prompt(subject: str, num_questions: int, difficulty: str) -> tuple[str, str]:
    """Validate inputs and construct (prompt, system_instruction) for MCQ generation."""
    cleaned_subject = validate_non_empty_text(subject, "Quiz topic")
    validated_count = validate_question_count(num_questions)
    if difficulty not in QUIZ_DIFFICULTIES:
        raise ValidationError(f"Unsupported difficulty '{difficulty}'.")

    prompt = (
        f"Create {validated_count} multiple choice questions on topic "
        f"'{cleaned_subject}' at difficulty '{difficulty}'.\n"
        "Output ONLY a valid JSON array of objects without markdown code fences.\n"
        "Each object must follow this exact structure:\n"
        "{\n"
        '  "id": 1,\n'
        '  "question": "Question text?",\n'
        '  "options": ["Option A", "Option B", "Option C", "Option D"],\n'
        '  "answer": "Option A",\n'
        '  "explanation": "Detailed explanation of why Option A is correct."\n'
        "}\n"
        'The "answer" field must exactly match one of the strings in "options".'
    )
    system_instruction = (
        "You are an automated quiz generator engine. Return raw valid JSON array only."
    )
    return prompt, system_instruction


def _strip_code_fences(raw_text: str) -> str:
    """Remove leading/trailing markdown code fences if present."""
    text = raw_text.strip()
    if text.startswith("```"):
        first_newline = text.find("\n")
        if first_newline != -1:
            text = text[first_newline + 1 :]
        else:
            text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    return text.strip()


def _extract_balanced_json_array(raw_text: str) -> str | None:
    """Find the first balanced JSON array `[...]` in raw_text, respecting strings."""
    start = raw_text.find("[")
    if start == -1:
        return None

    depth = 0
    in_string = False
    escape = False
    for idx in range(start, len(raw_text)):
        ch = raw_text[idx]
        if escape:
            escape = False
            continue
        if ch == "\\" and in_string:
            escape = True
            continue
        if ch == '"':
            in_string = not in_string
            continue
        if in_string:
            continue
        if ch == "[":
            depth += 1
        elif ch == "]":
            depth -= 1
            if depth == 0:
                return raw_text[start : idx + 1]
    return None


def parse_and_validate_quiz(raw_text: str) -> list[QuizQuestion]:
    """Parse raw model text into a validated list of QuizQuestion objects."""
    if not isinstance(raw_text, str) or not raw_text.strip():
        raise QuizParseError("AI returned empty quiz output.")

    cleaned = _strip_code_fences(raw_text)
    parsed: object = None
    try:
        parsed = json.loads(cleaned)
    except json.JSONDecodeError as first_exc:
        candidate = _extract_balanced_json_array(raw_text)
        if candidate is None:
            raise QuizParseError("Could not locate a JSON array in the AI output.") from first_exc
        try:
            parsed = json.loads(candidate)
        except json.JSONDecodeError as exc:
            raise QuizParseError("AI output contained malformed JSON.") from exc

    if not isinstance(parsed, list) or len(parsed) == 0:
        raise QuizParseError("Quiz JSON must be a non-empty list of question objects.")

    validated: list[QuizQuestion] = []
    seen_questions: set[str] = set()

    for idx, item in enumerate(parsed, start=1):
        if not isinstance(item, dict):
            raise QuizParseError(f"Question #{idx} is not a JSON object.")

        q_text = item.get("question")
        if not isinstance(q_text, str) or not q_text.strip():
            raise QuizParseError(f"Question #{idx} is missing a valid 'question' string.")
        q_clean = q_text.strip()

        raw_options = item.get("options")
        if not isinstance(raw_options, list) or len(raw_options) < 2:
            raise QuizParseError(
                f"Question #{idx} must have a 'options' list with at least 2 choices."
            )
        options = tuple(
            opt.strip() for opt in raw_options if isinstance(opt, str) and opt.strip()
        )
        if len(options) < 2:
            raise QuizParseError(f"Question #{idx} has fewer than 2 valid text options.")

        raw_answer = item.get("answer")
        if not isinstance(raw_answer, str) or not raw_answer.strip():
            raise QuizParseError(f"Question #{idx} is missing a valid 'answer' string.")
        ans_clean = raw_answer.strip()

        if ans_clean not in options:
            # Controlled recovery: case-insensitive match against options
            lower_map = {opt.lower(): opt for opt in options}
            if ans_clean.lower() in lower_map:
                ans_clean = lower_map[ans_clean.lower()]
            else:
                raise QuizParseError(
                    f"Question #{idx} answer '{ans_clean}' does not match any option."
                )

        raw_expl = item.get("explanation")
        expl_clean = (
            raw_expl.strip()
            if isinstance(raw_expl, str) and raw_expl.strip()
            else "No explanation provided."
        )

        norm_key = q_clean.lower()
        if norm_key in seen_questions:
            continue
        seen_questions.add(norm_key)

        validated.append(
            QuizQuestion(
                id=len(validated) + 1,
                question=q_clean,
                options=options,
                answer=ans_clean,
                explanation=expl_clean,
            )
        )

    if not validated:
        raise QuizParseError("No valid questions remained after validation.")
    return validated


def evaluate_quiz(
    questions: list[QuizQuestion], user_answers: dict[int, str | None]
) -> QuizEvaluation:
    """Score user answers against validated QuizQuestion objects."""
    if not questions:
        raise ValidationError("Cannot evaluate an empty quiz.")

    results: list[QuestionResult] = []
    score = 0
    for idx, item in enumerate(questions):
        chosen = user_answers.get(idx)
        is_correct = chosen == item.answer
        if is_correct:
            score += 1
        results.append(
            QuestionResult(
                question_number=idx + 1,
                question=item.question,
                user_answer=chosen,
                correct_answer=item.answer,
                is_correct=is_correct,
                explanation=item.explanation,
            )
        )

    total = len(questions)
    percentage = int((score / total) * 100)
    return QuizEvaluation(
        score=score,
        total=total,
        percentage=percentage,
        passed=percentage >= QUIZ_PASS_THRESHOLD_PCT,
        results=tuple(results),
    )
