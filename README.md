# 🎓 AI-Powered Study Buddy

> **IBM SkillsBuild & Edunet Foundation Capstone Project**  
> *Personalized 24/7 Generative AI Virtual Companion for Students*

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)
![Streamlit](https://img.shields.io/badge/UI-Streamlit-FF4B4B?logo=streamlit)
![Gemini AI](https://img.shields.io/badge/AI_Model-Google_Gemini_2.5_Flash-8E44AD?logo=google)
![License](https://img.shields.io/badge/License-MIT-green)

---

## 📌 Project Overview

**AI-Powered Study Buddy** is a personalized, interactive virtual tutor powered by **Google Gemini 2.5 Flash** and built using **Streamlit**. It addresses key challenges in self-study by delivering on-demand explanations, document summarization (including PDF support), automated MCQ quizzes, and productivity tools.

---

## 🌟 Key Features

1. **💡 Topic Explainer (ELI5 & Analogies):**
   - Simplifies complex topics using relatable real-world analogies.
   - Generates step-by-step breakdowns, key takeaways, and self-test reflection questions.
   - Includes instant **Markdown (.md) Download** button.

2. **📝 Notes & Document Summarizer (PDF Support):**
   - Supports direct text input and document file uploads (`.pdf`, `.txt`, `.md`, `.py`).
   - Extracts text automatically from PDF textbooks/notes using `pypdf`.
   - Offers multiple output formats: Bullet points, Executive Overview, Flashcard Q&A, and Code Debugging.

3. **🧠 Interactive MCQ Quiz Generator:**
   - Dynamically generates multiple-choice quizzes with real-time score tracking.
   - Uses regex-assisted JSON extraction to guarantee reliable parsing.
   - Features collapsible `st.expander` answer keys and detailed explanations.

4. **⏱️ Study Planner & Pomodoro Timer:**
   - Includes presets for 25-min Focus Sessions, 5-min Short Breaks, and 15-min Long Breaks.
   - Interactive daily study task goal checklist with task completion tracking.

5. **ℹ️ Architecture & Documentation:**
   - System workflow diagram, tech stack overview, and project submission metadata.

---

## 🏗️ System Workflow Architecture

```
┌────────────────────────┐      ┌─────────────────────────┐      ┌────────────────────────┐
│  User Streamlit UI     │ ---> │  Python App Logic       │ ---> │  Google Gemini 2.5     │
│  (Topic / Notes / Quiz)│      │  (dotenv / PyPDF / JSON)│      │  Flash Generative API  │
└────────────────────────┘      └─────────────────────────┘      └────────────────────────┘
             │                                                            │
             ▼                                                            ▼
┌────────────────────────┐                                   ┌────────────────────────┐
│ Scorecards / Downloads │ <-------------------------------- │ Structured Output      │
│ & Interactive Timers   │                                   │ (Markdown / JSON MCQs) │
└────────────────────────┘                                   └────────────────────────┘
```

---

## 🚀 Quick Start Guide

### 1. Clone the Repository
```bash
git clone https://github.com/Kunal77744/AI-Study-Buddy.git
cd AI-Study-Buddy
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure API Key
Create a `.env` file in the project root directory or pass it directly in the Streamlit sidebar developer settings:
```env
GEMINI_API_KEY=your_google_gemini_api_key_here
```

### 4. Run the Web Application
```bash
streamlit run app.py
```
Open your browser and navigate to `http://localhost:8501`.

---

## 👨‍🎓 Project Credits & Submission

- **Student Name:** Kunal Deshmukh
- **Department:** Information Technology (IT), USICT
- **Track:** Artificial Intelligence
- **Capstone Program:** IBM SkillsBuild & Edunet Foundation
- **GitHub Repository:** [https://github.com/Kunal77744/AI-Study-Buddy](https://github.com/Kunal77744/AI-Study-Buddy)

---

## 📜 License
This project is open-source under the [MIT License](LICENSE).
