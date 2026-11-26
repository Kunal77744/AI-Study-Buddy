"""Unit tests for services.quiz_service."""

import pytest

from services.quiz_service import (
    QuizQuestion,
    build_quiz_prompt,
    evaluate_quiz,
    parse_and_validate_quiz,
)
from utils.exceptions import QuizParseError, ValidationError


def test_build_quiz_prompt_valid() -> None:
    prompt, sys_inst = build_quiz_prompt("DBMS", 3, "Medium")
    assert "3 multiple choice questions" in prompt
    assert "DBMS" in prompt
    assert "JSON array" in sys_inst


def test_build_quiz_prompt_invalid_topic() -> None:
    with pytest.raises(ValidationError):
        build_quiz_prompt("  ", 3, "Easy")


def test_parse_and_validate_quiz_with_markdown_fences_and_extra_text() -> None:
    raw = """Here is your quiz:
```json
[
  {
    "id": 1,
    "question": "What does SQL stand for?",
    "options": ["Structured Query Language", "Simple Query List", "System Query Logic", "None"],
    "answer": "structured query language",
    "explanation": "SQL stands for Structured Query Language."
  }
]
```
Hope that helps [note]"""
    questions = parse_and_validate_quiz(raw)
    assert len(questions) == 1
    assert questions[0].answer == "Structured Query Language"


def test_parse_and_validate_quiz_rejects_malformed_json() -> None:
    with pytest.raises(QuizParseError, match="malformed JSON"):
        parse_and_validate_quiz('[{"question": "Broken",]')


@pytest.mark.parametrize(
    "payload",
    [
        '[{"options": ["A", "B"], "answer": "A"}]',
        '[{"question": "Q1?", "options": ["OnlyOne"], "answer": "OnlyOne"}]',
        '[{"question": "Q1?", "options": ["A", "B"]}]',
    ],
)
def test_parse_and_validate_quiz_rejects_missing_fields(payload: str) -> None:
    with pytest.raises(QuizParseError):
        parse_and_validate_quiz(payload)


def test_parse_and_validate_quiz_rejects_missing_answer_match() -> None:
    raw = '[{"question": "Q1?", "options": ["A", "B"], "answer": "Z", "explanation": "Because"}]'
    with pytest.raises(QuizParseError, match="does not match any option"):
        parse_and_validate_quiz(raw)


def test_parse_and_validate_quiz_rejects_non_list() -> None:
    with pytest.raises(QuizParseError, match="non-empty list"):
        parse_and_validate_quiz('{"question": "Q1?"}')


def test_parse_and_validate_quiz_deduplicates_questions() -> None:
    raw = """[
      {"question": "What is 2+2?", "options": ["3", "4"], "answer": "4", "explanation": "Math"},
      {"question": "What is 2+2?", "options": ["3", "4"], "answer": "4", "explanation": "Math"}
    ]"""
    questions = parse_and_validate_quiz(raw)
    assert len(questions) == 1


def test_evaluate_quiz_scoring() -> None:
    questions = [
        QuizQuestion(1, "Q1", ("A", "B"), "A", "Exp1"),
        QuizQuestion(2, "Q2", ("C", "D"), "D", "Exp2"),
    ]
    evaluation = evaluate_quiz(questions, {0: "A", 1: "C"})
    assert evaluation.score == 1
    assert evaluation.total == 2
    assert evaluation.percentage == 50
    assert evaluation.passed is False
    assert evaluation.results[0].is_correct is True
    assert evaluation.results[1].is_correct is False
