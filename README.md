# 🎓 AI-Powered Study Buddy

> **IBM SkillsBuild & Edunet Foundation Capstone Project**  
> *Modular Generative AI Study Companion built with Python, Streamlit, and Google Gemini (`google-genai`)*

![Python](https://img.shields.io/badge/Python-3.11%2B-blue?logo=python)
![Streamlit](https://img.shields.io/badge/UI-Streamlit-FF4B4B?logo=streamlit)
![Gemini AI](https://img.shields.io/badge/AI-Google_Gemini-8E44AD?logo=google)
![Tests](https://img.shields.io/badge/Tested_with-pytest-0A9EDC?logo=pytest)

---

## 📌 Overview & Problem Statement

Students studying independently often face scattered search results, dense lecture PDFs, and a lack of immediate practice feedback. **AI-Powered Study Buddy** brings four focused study tools into one clean Streamlit workspace:

1. **💡 Topic Explainer:** Streams concept explanations tailored to audience level (`ELI5`, `High School Student`, `Undergraduate / Technical`, `Analogy-First Approach`) with `.md` export.
2. **📝 Notes & Document Summarizer:** Summarizes pasted text/code or uploaded `.pdf`, `.txt`, `.md`, `.py`, and `.json` files in multiple formats with session-cached extraction, chunked multi-section summarization, and prompt-delimiter sanitization.
3. **🧠 Interactive MCQ Quiz Generator:** Generates 1–10 MCQs using structured JSON output (`response_schema`), validates the schema, tracks answers in a form, and renders a scorecard with expandable explanations.
4. **🗺️ Personalized Study Roadmap:** Streams week-by-week learning roadmaps tailored to target duration (`1–8 Weeks`), skill level, and daily study hours with `.md` export.

---

## 🛠️ Technology Stack

- **Language:** Python 3.11+
- **UI Framework:** Streamlit (`streamlit>=1.30.0`)
- **AI SDK:** Official Google GenAI SDK (`google-genai>=1.0.0`)
- **PDF Extraction:** `pypdf>=4.0.0`
- **Configuration:** `python-dotenv>=1.0.0`
- **Testing & Linting (dev):** `pytest`, `ruff`

---

## 🏗️ Folder Structure

```text
AI-Study-Buddy/
├── app.py                      # Streamlit entry point & layout styling
├── config/
│   └── settings.py             # Centralized constants, model registry, key resolution
├── services/
│   ├── gemini_service.py       # Gemini API client (streaming, retries, structured output)
│   ├── pdf_service.py          # File validation, PDF/text extraction & chunking
│   ├── quiz_service.py         # Quiz prompting, JSON/schema validation, scoring
│   └── roadmap_service.py      # Study roadmap prompt builder & validation
├── components/
│   ├── sidebar.py              # Navigation sidebar & assistant readiness indicator
│   ├── topic_explainer.py      # Topic Explainer UI
│   ├── summarizer.py           # Notes & Document Summarizer UI
│   ├── quiz_ui.py              # Interactive MCQ Quiz UI
│   └── roadmap_ui.py           # Personalized Study Roadmap UI
├── utils/
│   ├── exceptions.py           # Custom StudyBuddyError hierarchy
│   ├── ui_errors.py            # Shared Streamlit error rendering helper
│   └── validators.py           # Input & upload validation
├── docs/                       # Architecture, security, testing & audit documentation
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

Unit and `AppTest` smoke tests mock external Gemini API calls so they run offline without consuming quota:
```bash
ruff check .
pytest -v
```
See [docs/TESTING.md](docs/TESTING.md) for the full test matrix and manual UI checklist.

---

## 🔒 Security & Privacy

- Never commit `.env` or API keys (`.gitignore` excludes `.env` and `.streamlit/secrets.toml`).
- Uploaded files are validated for extension (`.pdf`, `.txt`, `.md`, `.py`, `.json`), size (max `10 MB`), and PDF page count (max `50` pages).
- Document content is wrapped in sanitized `<document_content>` delimiters and capped/chunked before sending to Google's Gemini API. Do not upload confidential or sensitive personal data.
- See [docs/SECURITY.md](docs/SECURITY.md) for details.

---

## ⚠️ Known Limitations

- **Scanned / Image-Only PDFs:** OCR is not implemented; PDFs without selectable text are rejected with an informative message.
- **Session-Only State:** Generated explanations, summaries, quizzes, and roadmaps are stored in `st.session_state` and reset when the browser tab/session restarts.
- **No Built-In License File:** Add a `LICENSE` file if distributing under a specific open-source license.

---

## 👨‍🎓 Author

- **Kunal Deshmukh** — Department of Information Technology, USICT (Artificial Intelligence Track)
- **Capstone Program:** IBM SkillsBuild & Edunet Foundation
