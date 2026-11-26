# Final Engineering Report — AI Study Buddy

**Branch:** `project-rescue` (branched from `main` at `06114d8`)  
**Status:** Refactored, linted, and unit-tested locally with mocked Gemini API calls. Not pushed to GitHub or merged into `main`.

---

## 1. Executive Summary
The monolithic 664-line `app.py` was refactored into a clean, modular Python/Streamlit architecture (`config/`, `utils/`, `services/`, `components/`, `tests/`) while preserving every existing feature: Topic Explainer, Notes & Document Summarizer (PDF/text/code), Interactive MCQ Quiz Generator, Pomodoro Timer & Daily Study Goals Checklist, and Architecture & Documentation tab.

---

## 2. Architecture (Original vs. Final)
- **Original:** Single `app.py` (664 lines) mixing CSS, environment loading, `pypdf` extraction, `google-generativeai` calls, JSON regex parsing, and 5 Streamlit tabs.
- **Final:**
  - `config/settings.py`: Centralized constants, `MODEL_OPTIONS`, upload/quiz/timer limits, and `resolve_api_key()`.
  - `utils/exceptions.py` & `utils/validators.py`: Typed `StudyBuddyError` hierarchy and input/file validators.
  - `services/`: Pure Python, Streamlit-independent modules (`gemini_service.py`, `pdf_service.py`, `quiz_service.py`, `timer_service.py`).
  - `components/`: Focused UI modules (`sidebar.py`, `topic_explainer.py`, `summarizer.py`, `quiz_ui.py`, `study_planner.py`, `architecture_tab.py`).
  - `app.py`: Clean entry point (162 lines) wiring page config, minimal CSS, sidebar, hero banner, and 5 tabs.

---

## 3. Bugs Fixed
1. **Model Routing Bug (`app.py` line 199 → `services/gemini_service.py`):** Replaced `"gemini-1.5-flash" if "1.5" in model_name` with explicit `MODEL_OPTIONS` lookup in `resolve_model_id()`, so `gemini-1.5-pro` is no longer routed to `gemini-1.5-flash`, and updated `components/sidebar.py` to display the actual active model.
2. **Silent Error Swallowing & Broken `.md` Downloads (`app.py` lines 192–222 → `services/gemini_service.py`):** Replaced broad `except Exception` fallback and error-string returns with typed exceptions (`ConfigurationError`, `GeminiAuthError`, `GeminiRateLimitError`, `GeminiAPIError`), `request_options={"timeout": 30}`, and exponential-backoff retries only on transient errors.
3. **Quiz Schema & Stale Widget State (`app.py` lines 225–249, 488–503 → `services/quiz_service.py`, `components/quiz_ui.py`):** Added balanced JSON array extraction, strict schema validation (`question`, `options`, `answer` in `options`, `explanation`), deduplication, and `quiz_generation_id`-keyed radio widgets so new quizzes start unselected.
4. **Blocking Pomodoro Timer (`app.py` lines 565–576 → `services/timer_service.py`, `components/study_planner.py`):** Replaced synchronous `time.sleep(1)` loop with monotonic timestamp tracking (`time.monotonic()`) and `@st.fragment(run_every=1)` supporting Start, Pause, Resume, and Reset.
5. **PDF & File Edge Cases (`app.py` lines 162–183 → `services/pdf_service.py`, `components/summarizer.py`):** Added extension/size (`10 MB`) validation, `50`-page limit, encrypted/corrupted PDF handling, scanned/empty PDF detection, UTF-8 decode fallback, and `@st.cache_data` caching by `(filename, file_bytes)`.

---

## 4. Code Quality & UI/UX
- Added type hints, docstrings, and single-responsibility functions across all new modules.
- Simplified CSS in `app.py` for consistent contrast, spacing, and reduced decorative complexity while keeping the original theme.

---

## 5. Security
- Removed `.env` key pre-filling from the Developer Settings `st.text_input` widget (`components/sidebar.py`).
- Added privacy notice in the sidebar disclosing external Gemini API processing.
- Verified Git history (`git log --all -- .env`, `git log -S "AIza"`) contains no `.env` files or Google API keys.
- Added `.pytest_cache/` and `.ruff_cache/` to `.gitignore`.

---

## 6. Performance
- **Unmeasured / Structural Improvements:**
  - `@st.cache_data(max_entries=10)` in `components/summarizer.py` prevents re-parsing uploaded PDFs on unrelated UI reruns.
  - `@st.fragment(run_every=1)` in `components/study_planner.py` isolates timer ticks from full-page reruns.
  - No formal latency or memory benchmarks were executed.

---

## 7. Testing & Verification
Executed after final code edits:
- `ruff check .` → **Passed** (`All checks passed!`)
- `pytest -v` → **34 passed, 0 failed** (`tests/test_validators.py`, `tests/test_pdf_service.py`, `tests/test_gemini_service.py`, `tests/test_quiz_service.py`, `tests/test_timer_service.py`, `tests/test_app_smoke.py`).
- **Untested / Not Verified:**
  - Live end-to-end Google Gemini API calls (all Gemini unit tests used mocks; no live API key was exercised).
  - Interactive browser visual inspection of Streamlit UI.

---

## 8. Dependencies
- `requirements.txt` contains only directly used runtime dependencies (`streamlit>=1.30.0`, `google-generativeai>=0.4.0`, `python-dotenv>=1.0.0`, `pypdf>=4.0.0`). Unused `requests>=2.31.0` (left over from the removed REST fallback) was removed.
- Note: `google-generativeai 0.8.6` emits a deprecation `FutureWarning` recommending migration to `google-genai`. Migration was intentionally deferred as a future improvement because `google-genai` is not installed in the environment.

---

## 9. Documentation Created / Updated
- `AUDIT_REPORT.md`
- `ARCHITECTURE.md`
- `TESTING.md`
- `SECURITY.md`
- `LEARNING_GUIDE.md`
- `README.md`
- `FINAL_REPORT.md`

---

## 10. Run Instructions
```bash
pip install -r requirements.txt
# Configure GEMINI_API_KEY in .env (copy from .env.example)
streamlit run app.py
```

---

## 11. Git Changes
- **Branch:** `project-rescue`
- **Modified:** `app.py`, `README.md`, `.gitignore`
- **Created:** `pyproject.toml`, `config/`, `utils/`, `services/`, `components/`, `tests/`, `AUDIT_REPORT.md`, `ARCHITECTURE.md`, `TESTING.md`, `SECURITY.md`, `LEARNING_GUIDE.md`, `FINAL_REPORT.md`
- **Remote:** Not pushed; `main` untouched.
