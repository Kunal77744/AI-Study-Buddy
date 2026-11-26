# Testing & Verification Guide — AI Study Buddy

## 1. Test Stack
- **Test Runner:** `pytest` (configured in `pyproject.toml`)
- **Linter:** `ruff` (`E`, `F`, `I`, `UP`, `B` rules in `pyproject.toml`)
- **UI Smoke Test:** `streamlit.testing.v1.AppTest`

## 2. Running Automated Checks

```bash
# Run linter
ruff check .

# Run full test suite
pytest -v
```

## 3. Test Suites

| Test File | Scope | External Calls |
|---|---|---|
| `tests/test_validators.py` | API key resolution, non-empty text, question bounds, file metadata | None |
| `tests/test_pdf_service.py` | Plain-text extraction, empty/corrupted/blank PDFs, summary truncation | None (in-memory `pypdf.PdfWriter`) |
| `tests/test_gemini_service.py` | Model routing, missing key, auth/quota/timeout retries, `NotFound` | Mocked `google.generativeai` |
| `tests/test_quiz_service.py` | Prompt building, fenced/malformed JSON, schema validation, scoring | None |
| `tests/test_timer_service.py` | Start, pause, resume, reset, completion, `MM:SS` formatting | None (injected timestamps) |
| `tests/test_app_smoke.py` | Full `app.py` initialization & 5-tab render | None (no API call triggered) |

## 4. Manual UI Testing Checklist
Because live Gemini API calls require a valid `GEMINI_API_KEY` and visual layout inspection requires a browser:
1. Start the app: `streamlit run app.py`.
2. **Sidebar:** Switch between `gemini-2.5-flash`, `gemini-1.5-flash`, and `gemini-1.5-pro`; verify the "Active Model" badge updates to match.
3. **Topic Explainer:** Submit a topic and verify Markdown rendering + `.md` download.
4. **Summarizer:** Upload a text-based PDF and a blank/scanned PDF; verify text extraction succeeds for the first and shows a clear warning for the second.
5. **Quiz Generator:** Generate a quiz, submit answers, verify scorecard, then generate a *new* quiz and confirm radio buttons reset to unselected.
6. **Pomodoro Timer:** Start, Pause, Resume, and Reset while switching tabs or adding tasks to confirm the UI remains responsive.
