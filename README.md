# 🎓 AI-Powered Study Buddy

> **IBM SkillsBuild & Edunet Foundation Capstone Project**  
> *Modular Generative AI Study Companion built with Python, Streamlit, and Google Gemini*

![Python](https://img.shields.io/badge/Python-3.11%2B-blue?logo=python)
![Streamlit](https://img.shields.io/badge/UI-Streamlit-FF4B4B?logo=streamlit)
![Gemini AI](https://img.shields.io/badge/AI-Google_Gemini-8E44AD?logo=google)
![Tests](https://img.shields.io/badge/Tested_with-pytest-0A9EDC?logo=pytest)

---

## 📌 Overview & Problem Statement

Students studying independently often face scattered search results, dense lecture PDFs, and a lack of immediate practice feedback. **AI-Powered Study Buddy** brings four focused study tools into one clean Streamlit workspace:

1. **💡 Topic Explainer:** Explains concepts tailored to audience level (`ELI5`, `High School`, `Undergraduate / Technical`, `Analogy-First`) with `.md` export.
2. **📝 Notes & Document Summarizer:** Summarizes pasted text/code or uploaded `.pdf`, `.txt`, `.md`, `.py`, and `.json` files in multiple formats with cached extraction.
3. **🧠 Interactive MCQ Quiz Generator:** Generates 1–10 MCQs, validates the JSON schema, tracks answers in a form, and renders a scorecard with expandable explanations.
4. **⏱️ Study Planner & Pomodoro Timer:** Non-blocking timestamp-based Pomodoro timer (25/5/15-min presets, Start/Pause/Resume/Reset) paired with an in-session daily study goals checklist.

---

## 🛠️ Technology Stack

- **Language:** Python 3.11+
- **UI Framework:** Streamlit (`streamlit>=1.30.0`)
- **AI SDK:** Google Gemini (`google-generativeai>=0.4.0`) supporting `gemini-2.5-flash`, `gemini-1.5-flash`, and `gemini-1.5-pro`
- **PDF Extraction:** `pypdf>=4.0.0`
- **Configuration:** `python-dotenv>=1.0.0`
- **Testing & Linting (dev):** `pytest`, `ruff`

---

## 🏗️ Folder Structure

```text
AI-Study-Buddy/
├── app.py                      # Streamlit entry point
├── config/
│   └── settings.py             # Centralized constants, model options, key resolution
├── services/
│   ├── gemini_service.py       # Gemini API client (explicit models, timeout, retries)
│   ├── pdf_service.py          # File validation & PDF/text extraction
│   ├── quiz_service.py         # Quiz prompting, JSON/schema validation, scoring
│   └── timer_service.py        # Non-blocking Pomodoro state logic
├── components/
│   ├── sidebar.py              # Model selector, metadata, Developer Settings
│   ├── topic_explainer.py      # Tab 1 UI
│   ├── summarizer.py           # Tab 2 UI
│   ├── quiz_ui.py              # Tab 3 UI
│   ├── study_planner.py        # Tab 4 UI
│   └── architecture_tab.py     # Tab 5 UI
├── utils/
│   ├── exceptions.py           # Custom StudyBuddyError hierarchy
│   └── validators.py           # Input & upload validation
├── tests/                      # Automated pytest suite (mocked Gemini API)
├── .streamlit/config.toml      # Theme & server configuration
├── .env.example                # Environment variable template
├── pyproject.toml              # Pytest & Ruff configuration
└── requirements.txt            # Runtime dependencies
```

---

## 🚀 Installation & Running Locally

### 1. Clone & Navigate
```bash
git clone https://github.com/Kunal77744/AI-Study-Buddy.git
cd AI-Study-Buddy
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Gemini API Key
Copy `.env.example` to `.env` and add your key from [Google AI Studio](https://ai.google.dev):
```env
GEMINI_API_KEY=your_gemini_api_key_here
```
For Streamlit deployments, configure `GEMINI_API_KEY` in **Streamlit Secrets** (`.streamlit/secrets.toml` or cloud secrets). Credentials are read server-side and are never exposed in the student-facing UI.

### 4. Run the Application
```bash
streamlit run app.py
```
Open `http://localhost:8501` in your browser.

---

## 🧪 Testing

Unit tests mock all external Gemini API calls so they run offline without consuming quota:
```bash
ruff check .
pytest -v
```
See [TESTING.md](TESTING.md) for the full test matrix and manual UI checklist.

---

## 🔒 Security & Privacy

- Never commit `.env` or API keys (`.gitignore` excludes `.env` and `.streamlit/secrets.toml`).
- Uploaded files are validated for extension (`.pdf`, `.txt`, `.md`, `.py`, `.json`), size (max `10 MB`), and PDF page count (max `50` pages).
- Prompts and document excerpts (up to `15,000` characters) are sent to Google's Gemini API for processing. Do not upload confidential or sensitive personal data.
- See [SECURITY.md](SECURITY.md) for details.

---

## ⚠️ Known Limitations

- **Scanned / Image-Only PDFs:** OCR is not implemented; PDFs without selectable text are rejected with an informative message.
- **Session-Only Goals:** The Daily Study Goals checklist is stored in `st.session_state` and resets when the browser tab/session restarts.
- **Gemini SDK Deprecation:** `google-generativeai` is currently used for compatibility; migrating to the newer `google-genai` SDK is a planned future upgrade.
- **No Built-In License File:** Add a `LICENSE` file if distributing under a specific open-source license.

---

## 👨‍🎓 Author

- **Kunal Deshmukh** — Department of Information Technology, USICT (Artificial Intelligence Track)
- **Capstone Program:** IBM SkillsBuild & Edunet Foundation
