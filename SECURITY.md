# Security & Privacy Overview — AI Study Buddy

## 1. Secret Management
- API keys are loaded from `GEMINI_API_KEY` in `.env` (via `python-dotenv`) or entered optionally at runtime in the sidebar's **Developer Settings** (`type="password"`).
- `.env` and `.streamlit/secrets.toml` are excluded in `.gitignore`.
- The `.env` key is **never** pre-filled into UI input widgets, logged, or included in exception messages.
- Git history was checked during the audit (`git log --all -- .env` and `git log -S "AIza"`) with no committed `.env` files or Google API keys found.

## 2. Input & File Upload Controls
- Uploaded files are validated in `utils/validators.py` and `services/pdf_service.py`:
  - Allowed extensions: `.pdf`, `.txt`, `.md`, `.py`, `.json`
  - Maximum file size: `10 MB` (`MAX_FILE_SIZE_BYTES`)
  - Maximum PDF pages processed: `50` (`MAX_PDF_PAGES`)
  - Encrypted or corrupted PDFs raise `FileProcessingError` cleanly without exposing stack traces.
- Text sent to the Gemini API for summarization is capped at `15,000` characters (`MAX_SUMMARY_INPUT_CHARS`).

## 3. External AI Processing & Privacy Notice
- Any topic, pasted note, or extracted document excerpt submitted by the user is transmitted to Google's Gemini API for generation.
- A privacy notice is displayed in the sidebar (`components/sidebar.py`). Users should avoid uploading confidential, regulated, or personally identifiable documents.

## 4. Known Dependency & Security Notes
- `google-generativeai` (`0.8.6`) emits a deprecation `FutureWarning` advising migration to `google-genai`. Migrating to `google-genai` is recommended as a future upgrade once installed and tested.
- No formal compliance certification (GDPR, SOC 2, ISO 27001) is claimed.
