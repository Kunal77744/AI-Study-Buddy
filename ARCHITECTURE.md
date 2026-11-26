# Architecture Documentation — AI Study Buddy

## 1. Design Goals
The application was refactored from a 664-line monolithic `app.py` into a modular, layered Python/Streamlit architecture that remains approachable for a junior developer:
- **Separation of concerns:** UI rendering (`components/`), business/API/file logic (`services/`), shared validation/errors (`utils/`), and constants/configuration (`config/`) are cleanly separated.
- **Testability:** All services (`pdf_service`, `quiz_service`, `timer_service`, `gemini_service`) are pure Python modules with zero Streamlit imports, enabling fast unit testing with `pytest`.
- **No circular imports:** Dependency direction flows strictly downward:
  `app.py` → `components/` → `services/` → `utils/` & `config/`

## 2. Directory Structure

```text
AI-Study-Buddy/
├── app.py                      # Streamlit entry point, page config, CSS, tab wiring
├── config/
│   └── settings.py             # Model registry, limits, presets, API key resolution
├── services/
│   ├── gemini_service.py       # Explicit model routing, timeouts, retries, error mapping
│   ├── pdf_service.py          # File validation, pypdf extraction, page/char limits
│   ├── quiz_service.py         # Prompt building, JSON extraction, schema validation, scoring
│   └── timer_service.py        # Non-blocking monotonic timestamp Pomodoro state machine
├── components/
│   ├── sidebar.py              # Model selector, metadata, Developer Settings override
│   ├── topic_explainer.py      # Tab 1: Topic Explainer + Markdown download
│   ├── summarizer.py           # Tab 2: Notes/PDF Summarizer + @st.cache_data extraction
│   ├── quiz_ui.py              # Tab 3: Interactive MCQ Quiz + scorecard + answer key
│   ├── study_planner.py        # Tab 4: Non-blocking Pomodoro fragment + goals checklist
│   └── architecture_tab.py     # Tab 5: In-app architecture & credits view
├── utils/
│   ├── exceptions.py           # Domain exception hierarchy (StudyBuddyError base)
│   └── validators.py           # Text, question count, and file metadata validators
└── tests/                      # Automated pytest suite (mocked API calls)
```

## 3. Key Architectural Decisions
1. **Explicit Model Routing (`services/gemini_service.py`):** `resolve_model_id()` maps UI labels directly to exact Gemini model IDs (`gemini-2.5-flash`, `gemini-1.5-flash`, `gemini-1.5-pro`) and raises `ConfigurationError` or `GeminiAPIError` instead of silently substituting models.
2. **Non-Blocking Pomodoro (`services/timer_service.py` + `components/study_planner.py`):** Replaced the synchronous `time.sleep(1)` loop with monotonic timestamp tracking (`time.monotonic()`) paired with Streamlit's `@st.fragment(run_every=1)` when `status == "running"`.
3. **Quiz State Isolation (`components/quiz_ui.py`):** Uses an incrementing `quiz_generation_id` in widget keys (`quiz_{gen_id}_opt_{idx}`) so regenerating a quiz never inherits radio selections from a previous quiz.
4. **Scoped PDF Caching (`components/summarizer.py`):** Uses `@st.cache_data(max_entries=10)` keyed by `(filename, file_bytes)` so changing summary options does not re-parse the PDF on every rerun.
