# Security & Privacy Overview — AI Study Buddy

## 1. Secret Management
- API keys are loaded server-side from `GEMINI_API_KEY` in `.env` (via `python-dotenv`) or Streamlit Secrets (`st.secrets`).
- `.env` and `.streamlit/secrets.toml` are excluded in `.gitignore`.
- API keys are **never** pre-filled into UI input widgets, logged, or included in exception messages (`_SECRET_PATTERN` redacts key-like tokens in diagnostic logs).

## 2. Input & File Upload Controls
- Text inputs (`Topic`, `Quiz Topic`, `Learning Goal`) are bounded to `200` characters in the UI and validated non-empty via `utils/validators.py`.
- Uploaded files are validated in `utils/validators.py` and `services/pdf_service.py`:
  - Allowed extensions: `.pdf`, `.txt`, `.md`, `.py`, `.json`
  - Maximum file size: `10 MB` (`MAX_FILE_SIZE_BYTES`)
  - Maximum PDF pages processed: `50` (`MAX_PDF_PAGES`)
  - Encrypted or corrupted PDFs raise `FileProcessingError` cleanly without exposing stack traces.
- Summarizer content is chunked at `15,000` characters per section (up to 3 sections) and wrapped in sanitized `<document_content>` delimiters to mitigate prompt-delimiter breakout.

## 3. External AI Processing & Privacy Notice
- Any topic, pasted note, or extracted document excerpt submitted by the user is transmitted to Google's Gemini API via the official `google-genai` SDK.
- Users should avoid uploading confidential, regulated, or personally identifiable documents.
- No formal compliance certification (GDPR, SOC 2, ISO 27001) is claimed.
