# 🎓 AI-Powered Study Buddy

> **IBM SkillsBuild & Edunet Foundation Capstone Project**  
> *Personalized 24/7 Generative AI Virtual Companion for Students*

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)
![Streamlit](https://img.shields.io/badge/UI-Streamlit-FF4B4B?logo=streamlit)
![Gemini AI](https://img.shields.io/badge/AI_Model-Google_Gemini_2.5_Flash-8E44AD?logo=google)
![License](https://img.shields.io/badge/License-MIT-green)

---

## 📌 Project Overview

**AI-Powered Study Buddy** solves the challenges students face during self-study hours. It acts as an interactive, 24/7 learning assistant powered by **Google Gemini 2.5 Flash** and built with a responsive **Streamlit** interface.

### 🌟 Key Features

1. **💡 Explain a Topic (ELI5 & Analogies):**
   - Simplifies complex topics using relatable real-world analogies (Explain Like I'm 10).
   - Generates step-by-step breakdowns, key takeaways, and reflection questions.

2. **📝 Notes & Code Summarizer:**
   - Summarizes long notes, textbook passages, or code snippets into clean bullet points.
   - Accepts direct text input or file uploads (`.txt`, `.md`, `.py`).

3. **🧠 Interactive MCQ Quiz Generator:**
   - Dynamically generates multiple-choice quizzes for any subject and difficulty.
   - Features real-time score tracking, session state management, and collapsible `st.expander` answer explanations.

4. **⏱️ Study Planner & Pomodoro Timer:**
   - 25-minute interactive study timer with task checklists to maintain focus.

5. **ℹ️ Capstone Metadata & Project Info:**
   - Complete problem statement, architecture, system approach, and references.

---

## 🛠️ Tech Stack & Architecture

- **Frontend / Web UI:** Streamlit (`streamlit`)
- **Generative AI API:** Google Gemini 2.5 Flash (`google-generativeai`)
- **Environment Management:** `python-dotenv`
- **Deployment Target:** Localhost (`http://localhost:8501`) / Streamlit Community Cloud

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
Create a `.env` file in the project root directory or pass it directly in the Streamlit sidebar:
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
