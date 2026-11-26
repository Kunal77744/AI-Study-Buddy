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
| `tests/test_pdf_service.py` | Plain-text extraction, empty/corrupted/blank PDFs, summary truncation & chunking | None (in-memory `pypdf.PdfWriter`) |
| `tests/test_gemini_service.py` | Model routing, missing key, auth/quota/timeout retries, streaming, structured JSON | Mocked `google.genai.Client` |
| `tests/test_quiz_service.py` | Prompt building, fenced/malformed JSON, schema validation, scoring | None |
| `tests/test_roadmap_service.py` | Roadmap prompt construction and input validation | None |
| `tests/test_app_smoke.py` | Full `app.py` initialization & 4-section render + mocked UI flows | None (mocked `stream_text` / `generate_text`) |

## 4. Manual UI Testing Checklist
1. Start the app: `streamlit run app.py`.
2. **Topic Explainer:** Submit a topic, verify streaming output, `.md` download, and Clear button.
3. **Summarizer:** Upload a text-based PDF and a blank/scanned PDF; verify text extraction succeeds for the first and shows a clear warning for the second.
4. **Quiz Generator:** Generate a quiz, submit answers, verify scorecard (including unanswered warning), then generate a *new* quiz and confirm radio buttons reset to unselected.
5. **Study Roadmap:** Generate a roadmap for a goal/duration/level, verify streaming output, `.md` download, and Clear button.
