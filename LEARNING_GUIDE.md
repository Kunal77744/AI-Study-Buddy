# Developer Learning Guide — AI Study Buddy

This guide explains how **AI Study Buddy** works under the hood so you can confidently explain, debug, and extend every part of the project in code reviews or technical interviews.

---

## 1. Project Architecture Explanation
Instead of keeping all 664 lines in `app.py`, the app follows a simple 4-layer structure:
- **`config/settings.py`**: Single source of truth for constants (model IDs, file limits, timer presets) and `resolve_api_key()`.
- **`utils/`**: Shared domain exceptions (`exceptions.py`) and input/file validators (`validators.py`).
- **`services/`**: Pure Python business logic—PDF reading, Gemini API calls, quiz parsing/scoring, and timer math. None of these files import `streamlit`, which makes them fast and easy to unit-test.
- **`components/` & `app.py`**: Streamlit UI modules that collect user inputs, call `services/`, catch `StudyBuddyError`, and render outputs.

---

## 2. Module & Function Responsibilities
- **`config/settings.py`**: `MODEL_OPTIONS`, `AppMetadata`, `resolve_api_key(override_key)`.
- **`utils/exceptions.py`**: `StudyBuddyError` base class with specific subclasses (`ConfigurationError`, `ValidationError`, `FileProcessingError`, `GeminiAPIError`, `GeminiAuthError`, `GeminiRateLimitError`, `QuizParseError`).
- **`utils/validators.py`**: `validate_non_empty_text()`, `validate_question_count()`, `validate_uploaded_file_metadata()`.
- **`services/gemini_service.py`**: `resolve_model_id()`, `_extract_response_text()`, `generate_text()`.
- **`services/pdf_service.py`**: `extract_text_from_bytes()`, `_extract_pdf_text()`, `_extract_plain_text()`, `prepare_text_for_summary()`.
- **`services/quiz_service.py`**: `build_quiz_prompt()`, `_extract_balanced_json_array()`, `parse_and_validate_quiz()`, `evaluate_quiz()`.
- **`services/timer_service.py`**: `PomodoroState`, `start_timer()`, `pause_timer()`, `resume_timer()`, `reset_timer()`, `get_remaining_seconds()`, `sync_timer_state()`.

---

## 3. Application Execution Flow
1. User opens the app (`streamlit run app.py`).
2. `app.py` configures the page, injects minimal CSS, and calls `render_sidebar()` to get `(model_choice, custom_key)`.
3. Each of the 5 `st.tabs` delegates to its component in `components/`.
4. When the user clicks an action button (e.g., **Explain Concept**, **Summarize Document**, **Generate Custom Quiz**), the component validates inputs, calls `services/`, stores results in `st.session_state`, and renders the output.

---

## 4. Key Workflows

### Gemini API Workflow (`services/gemini_service.py`)
1. `validate_non_empty_text()` ensures the prompt isn't blank.
2. `resolve_api_key()` checks the sidebar override first, then `GEMINI_API_KEY` from `.env`.
3. `resolve_model_id()` maps the UI label to the exact Gemini model ID (never silently switching models).
4. `model.generate_content(..., request_options={"timeout": 30})` runs with exponential-backoff retries **only** for transient errors (`DeadlineExceeded`, `ServiceUnavailable`, `TimeoutError`, `ConnectionError`). Auth (`Unauthenticated`) and quota (`ResourceExhausted`) errors fail immediately with clear messages.

### PDF Processing Workflow (`services/pdf_service.py` + `components/summarizer.py`)
1. `@st.cache_data` in `components/summarizer.py` caches extraction by `(filename, file_bytes)` so changing summary sliders doesn't re-parse the PDF.
2. `validate_uploaded_file_metadata()` checks allowed extensions and the 10 MB limit.
3. `pypdf.PdfReader` checks for corruption and encryption, reads up to 50 pages, and raises `FileProcessingError` if extracted text is under 20 characters (detecting scanned/image-only PDFs).

### Quiz Generation Workflow (`services/quiz_service.py` + `components/quiz_ui.py`)
1. `build_quiz_prompt()` constructs a strict JSON-array prompt.
2. `parse_and_validate_quiz()` strips markdown fences, extracts a balanced `[...]` array if needed, validates every question (`question`, `options`, `answer` in `options`, `explanation`), deduplicates questions, and returns `list[QuizQuestion]`.
3. `quiz_generation_id` increments on each new quiz so radio widget keys (`quiz_{gen_id}_opt_{idx}`) start fresh.
4. `evaluate_quiz()` computes score, percentage, and pass/fail status (`>= 75%`).

### Non-Blocking Timer (`services/timer_service.py` + `components/study_planner.py`)
Instead of `time.sleep(1)` in a loop (which freezes Streamlit), `start_timer()` stores `end_timestamp = time.monotonic() + total_sec`. While `status == "running"`, `@st.fragment(run_every=1)` re-renders *only* the countdown display every second and computes `end_timestamp - time.monotonic()`.

---

## 5. Error Handling & Testing Strategy
- **Error Handling:** Services raise specific `StudyBuddyError` subclasses instead of returning error strings like `"❌ Error..."`. UI components catch `StudyBuddyError` and show `st.error(...)` without saving failed responses to `st.session_state` or offering broken `.md` downloads.
- **Testing:** `pytest` tests all services independently of Streamlit using `monkeypatch` / `MagicMock` for Gemini and in-memory `pypdf.PdfWriter` bytes for PDFs.

---

## 6. Interview Questions Based on This Codebase
1. **Why did you separate `services/` from `components/`?**  
   So business logic (PDF parsing, quiz validation, timer math, Gemini retries) has zero Streamlit dependency and can be unit-tested in milliseconds with `pytest`.
2. **How did you fix the blocking Pomodoro timer in Streamlit?**  
   By storing a monotonic `end_timestamp` in `PomodoroState` and using `@st.fragment(run_every=1)` to refresh only the timer widget instead of blocking the main thread with `time.sleep(1)`.
3. **Why shouldn't `except Exception:` silently fall back to another AI model?**  
   Silent fallbacks hide real bugs (like invalid API keys or typos in model names) and can change cost/quality without the user's knowledge. Explicit error classes (`GeminiAuthError`, `GeminiRateLimitError`) give actionable feedback.
4. **How do you prevent stale radio selections when a user generates a second quiz?**  
   By incrementing `st.session_state.quiz_generation_id` and including it in each radio widget's `key` (`f"quiz_{gen_id}_opt_{idx}"`).
5. **What happens if a user uploads a scanned PDF?**  
   `pypdf` extracts fewer than `MIN_MEANINGFUL_TEXT_CHARS` (20 chars), so `_extract_pdf_text()` raises `FileProcessingError` explaining that no selectable text was found and OCR is not supported.
