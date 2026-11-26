# Repository Audit Report — AI Study Buddy

**Repository:** `https://github.com/Kunal77744/AI-Study-Buddy`  
**Branch Audited:** `main` (commit `06114d8`) → Audit recorded on `project-rescue`  
**Audit Scope:** Complete read-only inspection of all 6 repository files and local Python environment. No source code was modified during this audit.

---

## Executive Summary

**AI-Powered Study Buddy** is a single-file (`app.py`, 664 lines) Streamlit web application built as an IBM SkillsBuild & Edunet Foundation Capstone project. It provides four student-facing tools—Topic Explainer, Notes & Document Summarizer (with PDF support), Interactive MCQ Quiz Generator, and Pomodoro Timer with a Daily Study Goals Checklist—plus an Architecture & Documentation tab.

While the core concept and UI layout are solid for a capstone prototype, the codebase has **critical reliability, state-management, and architectural issues** that affect correctness and maintainability:
- Model selection in `get_gemini_response` silently routes `gemini-1.5-pro` to `gemini-1.5-flash`.
- API errors and missing keys are returned as plain strings and treated as valid AI output (even offered for `.md` download).
- The Pomodoro timer uses a blocking `for ... time.sleep(1):` loop inside Streamlit's main thread, freezing the UI.
- Quiz JSON parsing lacks schema validation, and regenerating a quiz does not clear stale radio widget state.
- There are zero automated tests, no `LICENSE` file despite a README link, and all logic/UI/API code is coupled in `app.py`.

---

## A. Project Overview

- **What the application actually does:** Serves a Streamlit web dashboard (`app.py`) that sends user prompts (topics, pasted notes/code, extracted document text, quiz requests) to Google's Gemini API and renders Markdown responses, interactive MCQ forms, and a client-less Pomodoro countdown + task checklist.
- **Actual implemented features (verified in `app.py`):**
  1. **Topic Explainer (`tab1`, lines 311–361):** Accepts topic input, audience level (`ELI5`, `High School Student`, `Undergraduate / Technical`, `Analogy-First Approach`), and multi-select learning features; displays Markdown output and provides a `.md` download button.
  2. **Notes & Document Summarizer (`tab2`, lines 366–430):** Accepts pasted text/code or uploaded `.pdf`, `.txt`, `.md`, `.py`, `.json` files (`extract_text_from_file`), truncates content to `15,000` characters (`raw_content[:15000]`), and generates summaries in 4 formats and 3 detail levels with `.md` download.
  3. **Interactive MCQ Quiz Generator (`tab3`, lines 435–535):** Requests a JSON array of 1–10 MCQs from Gemini, parses it via `extract_json_quiz`, renders an `st.form` with radio buttons, calculates score/percentage on submission, and renders `st.expander` explanations.
  4. **Study Planner & Pomodoro Timer (`tab4`, lines 540–602):** Provides 25/5/15-minute timer presets and an in-memory daily study goals checklist (`st.session_state.goal_list`).
  5. **Architecture & Documentation (`tab5`, lines 607–660):** Static Markdown overview of problem statement, workflow diagram, tech stack, and project credits.
- **Target users:** Students and self-learners seeking on-demand concept explanations, note/PDF summaries, practice MCQs, and study focus tools.
- **Main execution flow:** `load_dotenv()` → `st.set_page_config()` → CSS injection → Sidebar (`model_choice`, `custom_key`) → Hero Banner → 5 `st.tabs` reading/writing `st.session_state` and calling `get_gemini_response()`.

---

## B. Technology Stack

Verified from `requirements.txt`, `app.py`, `.streamlit/config.toml`, and local `python --version` / `pip list`:

| Component | Declared (`requirements.txt`) | Local Environment (Verified) | Notes |
|---|---|---|---|
| Language | Python 3.10+ (per `README.md`) | `Python 3.11.6` | Compatible |
| Web UI | `streamlit>=1.30.0` | `streamlit 1.58.0` | Active |
| AI SDK | `google-generativeai>=0.4.0` | `google-generativeai 0.8.6` | Legacy SDK (REST fallback via `requests` if `ImportError`) |
| HTTP Client | `requests>=2.31.0` | `requests 2.34.2` | Used only in `ImportError` fallback |
| PDF Parser | `pypdf>=4.0.0` | `pypdf 6.14.2` | Used in `extract_text_from_file` |
| Env Config | `python-dotenv>=1.0.0` | `python-dotenv 1.2.2` | Loads `.env` at startup |
| Testing / Lint | *(Not in `requirements.txt`)* | `pytest 9.2.0`, `ruff 0.17.5` | Available locally, unused in repo |

---

## C. Architecture Review

- **Current Folder Structure:**
  - `app.py` (664 lines — entry point, CSS, config, API client, PDF parser, JSON parser, all 5 UI tabs)
  - `.streamlit/config.toml` (theme + server config)
  - `.env.example`, `.gitignore`, `requirements.txt`, `README.md`
- **Findings:**
  - **[High] Monolithic Coupling (`app.py`, lines 1–664):** Presentation, business logic, API communication, file parsing, and prompt templates are all in one file. Adding unit tests without refactoring is difficult because `app.py` executes Streamlit UI calls at module import time.
  - **[Medium] No Configuration Layer (`app.py`, lines 10, 190, 266–288):** Environment loading, model options, character limits (`15000`), and timer presets (`25`, `5`, `15`) are scattered inline.

---

## D. Code Quality Review

- **Large monolithic script:** `app.py` is 664 lines with inline HTML/CSS (`lines 21–159`), inline prompt strings, and deeply nested tab blocks.
- **Missing type hints:** None of the helper functions (`extract_text_from_file`, `get_gemini_response`, `extract_json_quiz`) have type annotations.
- **Poor exception handling:**
  - **[High] `app.py`, `get_gemini_response` (lines 201–222):** Broad `except Exception:` catches all SDK errors and silently falls back to `gemini-1.5-flash` without `system_instruction`. Errors return formatted strings (`"❌ **Processing Error**: ..."`) instead of raising typed exceptions.
  - **[Medium] `app.py`, `extract_text_from_file` (lines 177–183):** Returns `"❌ Error..."` strings, forcing callers to check `raw_content.startswith("❌")` (`line 384`).
- **Magic numbers & hardcoded strings:** `15000` character truncation (`line 412`), `75`% pass threshold (`line 512`), and hardcoded sidebar status (`line 264`).

---

## E. Functional Review

| Feature | Status | Evidence & Exact Location |
|---|---|---|
| Topic Explainer (`tab1`) | **Partially Working / Unverified Live** | Live API call not verified. Bug: error strings from `get_gemini_response` are saved to `st.session_state["last_explanation"]` (`line 348`) and offered for `.md` download (`line 356`). |
| Notes & PDF Summarizer (`tab2`) | **Partially Working / Unverified Live** | Live API & real PDF not verified. Bug: `decode("utf-8")` (`line 181`) fails on non-UTF-8 files; empty/scanned PDFs return `""` with no specific warning; `.json` is allowed in `st.file_uploader` (`line 380`) but not in the radio label (`line 370`). |
| Interactive MCQ Quiz (`tab3`) | **Broken Edge Cases / Unverified Live** | 1) `extract_json_quiz` (`lines 225–249`) does not validate item keys (`question`, `options`, `answer`, `explanation`) or option membership, risking `KeyError` at `lines 490–535`. 2) Regenerating a quiz does not clear `quiz_opt_{idx}` keys in `st.session_state`, leaking prior answers. 3) Greedy regex `r'\[\s*\{.*\}\s*\]'` (`line 243`) can over-match if extra brackets exist. |
| Pomodoro Timer (`tab4`) | **Broken UX** | `for current_sec in range(sec_total, -1, -1): ... time.sleep(1)` (`lines 567–572`) blocks Streamlit's script thread for up to 25 minutes, preventing normal UI interaction, pause/resume, or tab switching. |
| Daily Study Goals (`tab4`) | **Working (In-Memory Only)** | Checklist works via `st.session_state.goal_list` (`lines 583–602`), though state resets on browser refresh (expected for session-only storage). |
| Model Selector (`sidebar`) | **Broken** | `target_model = "gemini-1.5-flash" if "1.5" in model_name else "gemini-2.5-flash"` (`line 199`) routes `"gemini-1.5-pro"` to `"gemini-1.5-flash"`. Sidebar badge (`line 264`) always displays `Google Gemini 2.5 Flash`. |

*Note on Live Execution:* Live Gemini API responses and Streamlit browser rendering are **Not verified — additional inspection or execution required.**

---

## F. Security Review

- **[Low / Verified Clean] Git History & Secrets:** `git log --all -- .env` and `git log -S "AIza"` returned no `.env` files or API keys in Git history. `.gitignore` properly ignores `.env` and `.streamlit/secrets.toml`. Commit `ca85374` previously removed a private AICTE ID.
- **[Medium] API Key Handling in UI (`app.py`, line 287):** `custom_key = st.text_input(..., value=os.getenv("GEMINI_API_KEY", ""))` loads the environment API key into the Streamlit widget's initial value/state on every run, which is unnecessary when `.env` is already used as a fallback.
- **[Medium] Missing HTTP Timeout (`app.py`, line 216):** `requests.post(url, json=payload, ...)` has no `timeout`, risking an indefinite hang.
- **[Medium] Unbounded File Upload & Memory (`app.py`, lines 380–383):** `st.file_uploader` has no explicit size/page validation in code before reading/parsing PDFs, and large PDFs are extracted completely before slicing `[:15000]` (`line 412`).
- **[Low] Error Exposure & Privacy:** Raw `str(e)` or `res.text` is returned directly to the UI (`lines 220, 222`), and there is no user-facing notice that pasted/uploaded text is sent externally to Google's Gemini API.

---

## G. Performance Review

- **[High] Blocking Sleep Loop (`app.py`, lines 567–572):** `time.sleep(1)` in a synchronous loop holds the Streamlit worker thread continuously.
- **[Medium] Repeated PDF Extraction (`app.py`, lines 381–388):** Because `extract_text_from_file(uploaded_file)` runs on every Streamlit rerun while a file is selected in `st.file_uploader`, changing the summary format or detail slider re-parses the entire PDF from scratch.
- **[Low] Prompt/Rerun Efficiency:** `tab1` and `tab2` only call `get_gemini_response` inside `if st.button(...)`, which avoids duplicate API calls on unrelated reruns.

---

## H. Testing Review

- **Existing Tests:** None (`0` test files).
- **Missing Coverage:** Unit tests for configuration, PDF/text validation & extraction, Gemini API client (mocked), quiz JSON parsing & schema validation, quiz scoring, and Pomodoro timer state transitions.

---

## I. Documentation Review

- **[Medium] Broken License Link (`README.md`, line 100):** Links to `[MIT License](LICENSE)`, but no `LICENSE` file exists in the repository.
- **[Low] Minor Inaccuracies (`README.md`):**
  - Line 27 lists `.pdf`, `.txt`, `.md`, `.py` while `app.py` (`line 380`) also accepts `.json`.
  - No Testing section, no Security/Privacy disclosure, and no Known Limitations section.

---

## Proposed Architecture (Phase 2)

To separate concerns cleanly without over-engineering (preserving all existing features and keeping code approachable for a junior developer):

```text
AI-Study-Buddy/
├── app.py                      # Streamlit entry point, page config, CSS, tab orchestration
├── config/
│   ├── __init__.py
│   └── settings.py             # Constants, model configs, limits, env/secrets loading
├── services/
│   ├── __init__.py
│   ├── gemini_service.py       # Explicit model mapping, retries, timeouts, typed errors
│   ├── pdf_service.py          # File validation, size/page limits, PDF/text extraction
│   ├── quiz_service.py         # Prompting, JSON extraction, schema validation, scoring
│   └── timer_service.py        # Timestamp-based non-blocking Pomodoro state logic
├── components/
│   ├── __init__.py
│   ├── sidebar.py              # Model selector, metadata, safe API key override
│   ├── topic_explainer.py      # Tab 1 UI
│   ├── summarizer.py           # Tab 2 UI
│   ├── quiz_ui.py              # Tab 3 UI
│   ├── study_planner.py        # Tab 4 UI (non-blocking Pomodoro + checklist)
│   └── architecture_tab.py     # Tab 5 UI
├── utils/
│   ├── __init__.py
│   ├── exceptions.py           # Custom domain exceptions
│   └── validators.py           # Input & file validation helpers
├── tests/
│   ├── test_gemini_service.py
│   ├── test_pdf_service.py
│   ├── test_quiz_service.py
│   ├── test_timer_service.py
│   └── test_validators.py
├── .streamlit/config.toml
├── .env.example
├── .gitignore
├── requirements.txt
├── AUDIT_REPORT.md
├── ARCHITECTURE.md
├── TESTING.md
├── SECURITY.md
├── LEARNING_GUIDE.md
├── FINAL_REPORT.md
└── README.md
```
