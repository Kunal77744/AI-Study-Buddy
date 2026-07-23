import streamlit as st
import os
import json
import time
from dotenv import load_dotenv

# Load environment variables quietly from .env
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="AI Study Buddy | IBM SkillsBuild Capstone",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom High-End Professional CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Plus+Jakarta+Sans:wght@500;600;700;800&display=swap');
    
    * {
        font-family: 'Plus Jakarta Sans', 'Inter', sans-serif;
    }

    /* Hide Streamlit default header/footer elements for clean look */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Global background and styling */
    .stApp {
        background-color: #F8FAFC;
    }
    
    /* Main Hero Banner */
    .hero-banner {
        background: linear-gradient(135deg, #0F172A 0%, #1E293B 40%, #2563EB 100%);
        padding: 2.8rem 2.5rem;
        border-radius: 20px;
        color: #FFFFFF;
        margin-bottom: 2rem;
        box-shadow: 0 20px 25px -5px rgba(15, 23, 42, 0.15), 0 8px 10px -6px rgba(15, 23, 42, 0.1);
        position: relative;
        overflow: hidden;
    }
    
    .hero-banner h1 {
        font-size: 2.5rem;
        font-weight: 800;
        color: #FFFFFF !important;
        margin-bottom: 0.6rem;
        letter-spacing: -0.02em;
    }
    
    .hero-banner p {
        font-size: 1.05rem;
        color: #94A3B8;
        max-width: 800px;
        margin-bottom: 0;
        line-height: 1.6;
    }
    
    .badge-capstone {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: rgba(59, 130, 246, 0.15);
        border: 1px solid rgba(147, 197, 253, 0.3);
        color: #93C5FD;
        padding: 0.35rem 0.9rem;
        border-radius: 9999px;
        font-size: 0.82rem;
        font-weight: 600;
        margin-bottom: 1rem;
        letter-spacing: 0.03em;
        text-transform: uppercase;
    }
    
    /* Feature Container Card */
    .content-card {
        background: #FFFFFF;
        border-radius: 16px;
        padding: 2rem;
        border: 1px solid #E2E8F0;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.03), 0 2px 4px -2px rgba(0, 0, 0, 0.03);
        margin-bottom: 1.5rem;
    }
    
    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #FFFFFF;
        border-right: 1px solid #E2E8F0;
    }
    
    .sidebar-header {
        display: flex;
        align-items: center;
        gap: 12px;
        padding-bottom: 1rem;
        border-bottom: 1px solid #F1F5F9;
        margin-bottom: 1.2rem;
    }
    
    .sidebar-header h2 {
        font-size: 1.25rem;
        font-weight: 700;
        color: #0F172A;
        margin: 0;
    }
    
    /* Score Banner */
    .quiz-score-success {
        background: linear-gradient(135deg, #059669 0%, #10B981 100%);
        color: white;
        padding: 1.8rem;
        border-radius: 16px;
        text-align: center;
        margin-bottom: 1.8rem;
        box-shadow: 0 10px 15px -3px rgba(16, 185, 129, 0.2);
    }
    
    /* Streamlit Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #F1F5F9;
        padding: 6px;
        border-radius: 12px;
    }

    .stTabs [data-baseweb="tab"] {
        height: 44px;
        border-radius: 8px;
        font-weight: 600;
        font-size: 0.92rem;
        color: #64748B;
        border: none !important;
        padding: 0 18px;
    }

    .stTabs [aria-selected="true"] {
        background-color: #FFFFFF !important;
        color: #2563EB !important;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    }

    /* Button Customization */
    .stButton>button {
        background-color: #2563EB;
        color: #FFFFFF;
        border: none;
        border-radius: 10px;
        padding: 0.6rem 1.4rem;
        font-weight: 600;
        font-size: 0.95rem;
        transition: all 0.2s ease;
    }
    
    .stButton>button:hover {
        background-color: #1D4ED8;
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.25);
    }
</style>
""", unsafe_allow_html=True)

# Helper function to initialize Gemini API Client safely
def get_gemini_response(prompt, system_instruction=None, api_key=None, model_name="gemini-2.5-flash"):
    """
    Executes request using Gemini API (via environment variable or secure config fallback).
    """
    effective_api_key = api_key or os.getenv("GEMINI_API_KEY", "")
    
    # Fallback default key if env is empty
    if not effective_api_key:
        return "⚠️ **Configuration Notice**: Gemini API Key is loading from system environment. If you encounter issues, please check your `.env` configuration file."

    try:
        import google.generativeai as genai
        genai.configure(api_key=effective_api_key)
        
        target_model = "gemini-1.5-flash" if "1.5" in model_name else "gemini-2.5-flash"
        
        try:
            model = genai.GenerativeModel(target_model, system_instruction=system_instruction)
            response = model.generate_content(prompt)
            return response.text
        except Exception:
            model = genai.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content(prompt)
            return response.text

    except ImportError:
        import requests
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={effective_api_key}"
        payload = {
            "contents": [{"parts": [{"text": (system_instruction + "\n\n" if system_instruction else "") + prompt}]}]
        }
        res = requests.post(url, json=payload, headers={"Content-Type": "application/json"})
        if res.status_code == 200:
            return res.json()["candidates"][0]["content"]["parts"][0]["text"]
        else:
            return f"❌ **API Communication Error ({res.status_code})**: {res.text}"
    except Exception as e:
        return f"❌ **Processing Error**: {str(e)}"

# --- CLEAN & PROFESSIONAL SIDEBAR ---
with st.sidebar:
    st.markdown("""
    <div class="sidebar-header">
        <span style="font-size: 28px;">🎓</span>
        <div>
            <h2 style="font-size: 16px; margin:0;">AI Study Buddy Pro</h2>
            <span style="font-size: 12px; color: #64748B;">v2.5 Professional Edition</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("##### ⚙️ Active Engine Configuration")
    st.success("🟢 AI Engine: **Google Gemini 2.5 Flash**")
    
    # Model Selection (Clean Dropdown)
    model_choice = st.selectbox(
        "AI Processing Mode",
        ["gemini-2.5-flash (Recommended)", "gemini-1.5-flash", "gemini-1.5-pro"],
        index=0
    )

    st.divider()
    
    # Project Capstone Card
    st.markdown("### 📌 Submission Details")
    st.markdown("""
    **Project Title:** AI-Powered Study Buddy  
    **Author:** Kunal Deshmukh  
    **Institute:** USICT (IT Department)  
    **AICTE ID:** `STU6885e9f37bd011753606643`  
    **Capstone Partner:** IBM SkillsBuild & Edunet Foundation
    """)
    
    st.divider()

    # HIDDEN / ADVANCED DEVELOPER SETTINGS (Collapsed by default so it never clutter UI)
    with st.expander("🔐 Developer Settings", expanded=False):
        custom_key = st.text_input("Custom Gemini API Key Override", type="password", value=os.getenv("GEMINI_API_KEY", ""))
        st.caption("Leave empty to use default environment API configuration.")

# --- HERO BANNER ---
st.markdown("""
<div class="hero-banner">
    <div class="badge-capstone">🎓 IBM SkillsBuild & Edunet Foundation Capstone</div>
    <h1>AI-Powered Virtual Study Companion</h1>
    <p>Accelerate your learning journey with instant topic simplification, intelligent lecture note summarization, automated MCQ quizzes, and interactive focus tools.</p>
</div>
""", unsafe_allow_html=True)

# --- APPLICATION TABS ---
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "💡 Topic Explainer", 
    "📝 Notes & Code Summarizer", 
    "🧠 Interactive Quiz Generator", 
    "⏱️ Study Planner & Focus Timer", 
    "ℹ️ Project Documentation"
])

# ==========================================
# TAB 1: TOPIC EXPLAINER
# ==========================================
with tab1:
    st.markdown("### 💡 Explain Any Academic Concept")
    st.caption("Master complex subjects with intuitive explanations, real-world analogies, and step-by-step breakdowns.")
    
    col1, col2 = st.columns([2, 1])
    with col1:
        topic_input = st.text_input(
            "Enter Topic or Subject to Explore", 
            placeholder="e.g. Backpropagation, Quantum Entanglement, Normalization in DBMS, TCP/IP Model"
        )
    with col2:
        explanation_level = st.selectbox(
            "Target Audience Level",
            ["ELI5 (Explain Like I'm 10)", "High School Student", "Undergraduate / Technical", "Analogy-First Approach"],
            index=0
        )
    
    learning_options = st.multiselect(
        "Customize Explanation Features:",
        ["Real-World Analogy", "Step-by-Step Breakdown", "Key Formulas / Code Examples", "Self-Reflection Question"],
        default=["Real-World Analogy", "Step-by-Step Breakdown", "Self-Reflection Question"]
    )
    
    if st.button("🚀 Explain Concept", type="primary", use_container_width=True):
        if not topic_input.strip():
            st.warning("Please specify a topic to explain!")
        else:
            with st.spinner("AI Tutor is preparing your customized explanation..."):
                prompt = f"""
                Explain the topic: '{topic_input}' for target audience level: '{explanation_level}'.
                Include the following components in structured markdown format: {', '.join(learning_options)}.
                Ensure clean formatting with headings, bullet points, and bold text.
                """
                system_prompt = "You are an elite, encouraging AI Professor dedicated to making complex ideas crystal clear."
                
                response_text = get_gemini_response(prompt, system_instruction=system_prompt, api_key=custom_key, model_name=model_choice)
                
                st.markdown("---")
                st.markdown(response_text)

# ==========================================
# TAB 2: NOTES & CODE SUMMARIZER
# ==========================================
with tab2:
    st.markdown("### 📝 Notes & Source Code Summarizer")
    st.caption("Convert lengthy notes, textbook chapters, or programming code into high-retention structured summaries.")
    
    input_type = st.radio("Input Source:", ["Text / Code Snippet", "Upload File (.txt, .md, .py)"], horizontal=True)
    
    raw_content = ""
    if input_type == "Text / Code Snippet":
        raw_content = st.text_area(
            "Paste your notes or code here:",
            height=200,
            placeholder="Paste raw lecture notes, chapter passages, or source code snippets..."
        )
    else:
        uploaded_file = st.file_uploader("Choose a file to summarize", type=["txt", "md", "py", "json"])
        if uploaded_file is not None:
            raw_content = uploaded_file.read().decode("utf-8")
            st.success(f"File '{uploaded_file.name}' loaded successfully ({len(raw_content)} chars).")

    col_s1, col_s2 = st.columns(2)
    with col_s1:
        summary_format = st.selectbox(
            "Summary Output Format",
            ["Structured Bullet Points", "Executive Overview", "Flashcard Q&A Pairs", "Code Analysis & Debugging"]
        )
    with col_s2:
        detail_level = st.select_slider(
            "Summary Detail Level",
            options=["Concise (Key Highlights)", "Standard Balanced Summary", "In-Depth Detailed Analysis"]
        )
        
    if st.button("✨ Summarize Content", type="primary", use_container_width=True):
        if not raw_content.strip():
            st.warning("Please provide notes or content to summarize!")
        else:
            with st.spinner("Processing summary..."):
                prompt = f"""
                Summarize the following text in '{summary_format}' style with detail level '{detail_level}'.
                
                Source Content:
                \"\"\"
                {raw_content}
                \"\"\"
                """
                system_prompt = "You are a professional academic research assistant specializing in notes summarization."
                
                summary_output = get_gemini_response(prompt, system_instruction=system_prompt, api_key=custom_key, model_name=model_choice)
                
                st.markdown("---")
                st.markdown("#### 📋 Generated Summary Output")
                st.markdown(summary_output)

# ==========================================
# TAB 3: INTERACTIVE QUIZ GENERATOR
# ==========================================
with tab3:
    st.markdown("### 🧠 Interactive MCQ Quiz Generator")
    st.caption("Generate AI quizzes, test your understanding, and view real-time scores with detailed answer keys.")
    
    if "quiz_data" not in st.session_state:
        st.session_state.quiz_data = None
    if "user_answers" not in st.session_state:
        st.session_state.user_answers = {}
    if "quiz_submitted" not in st.session_state:
        st.session_state.quiz_submitted = False

    col_q1, col_q2, col_q3 = st.columns([2, 1, 1])
    with col_q1:
        quiz_subject = st.text_input("Quiz Topic / Subject", placeholder="e.g. Operating Systems, Data Structures, Machine Learning")
    with col_q2:
        num_q = st.number_input("Questions Count", min_value=1, max_value=10, value=4)
    with col_q3:
        difficulty = st.selectbox("Difficulty Level", ["Easy", "Medium", "Hard"])
        
    if st.button("🎯 Generate Custom Quiz", type="primary"):
        if not quiz_subject.strip():
            st.warning("Please specify a topic for the quiz!")
        else:
            with st.spinner(f"Generating {num_q} {difficulty} questions on '{quiz_subject}'..."):
                json_format_prompt = """
                Output ONLY a valid JSON array of objects without markdown formatted code fences. Each object must follow this structure:
                {
                    "id": 1,
                    "question": "Question text?",
                    "options": ["Option A", "Option B", "Option C", "Option D"],
                    "answer": "Option A",
                    "explanation": "Detailed explanation of why Option A is correct."
                }
                """
                prompt = f"Create {num_q} multiple choice questions on topic '{quiz_subject}' at difficulty '{difficulty}'. {json_format_prompt}"
                system_prompt = "You are an automated quiz generator engine. Return raw valid JSON array only."
                
                raw_res = get_gemini_response(prompt, system_instruction=system_prompt, api_key=custom_key, model_name=model_choice)
                
                clean_json = raw_res.strip()
                if clean_json.startswith("```json"):
                    clean_json = clean_json[7:]
                if clean_json.startswith("```"):
                    clean_json = clean_json[3:]
                if clean_json.endswith("```"):
                    clean_json = clean_json[:-3]
                clean_json = clean_json.strip()
                
                try:
                    st.session_state.quiz_data = json.loads(clean_json)
                    st.session_state.user_answers = {}
                    st.session_state.quiz_submitted = False
                    st.success("Quiz successfully generated!")
                except Exception as e:
                    st.error("Quiz parsing error. Raw output generated:")
                    st.code(raw_res)

    if st.session_state.quiz_data:
        st.markdown("---")
        st.markdown("#### 📝 Select Your Answers:")
        
        with st.form(key="interactive_quiz_form"):
            for idx, item in enumerate(st.session_state.quiz_data):
                st.markdown(f"**Q{idx+1}. {item['question']}**")
                chosen_opt = st.radio(
                    f"Options for Q{idx+1}:",
                    options=item["options"],
                    key=f"quiz_opt_{idx}",
                    index=None
                )
                st.session_state.user_answers[idx] = chosen_opt
                st.markdown("")
            
            submit_quiz = st.form_submit_button("🏆 Submit Quiz Answers", type="primary", use_container_width=True)
            if submit_quiz:
                st.session_state.quiz_submitted = True

    if st.session_state.get("quiz_submitted", False) and st.session_state.quiz_data:
        score = 0
        total = len(st.session_state.quiz_data)
        for idx, item in enumerate(st.session_state.quiz_data):
            if st.session_state.user_answers.get(idx) == item["answer"]:
                score += 1
                
        pct = int((score / total) * 100)
        
        st.markdown(f"""
        <div class="quiz-score-success">
            <h2 style="margin:0; font-size: 2rem;">Quiz Score: {score} / {total} ({pct}%)</h2>
            <p style="margin-top: 0.4rem; font-size: 1.1rem; opacity: 0.9;">{'🌟 Great job! Mastered the concept.' if pct >= 75 else '👍 Good effort! Check the answer review below.'}</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("#### 🔍 Answer Key & Explanations:")
        for idx, item in enumerate(st.session_state.quiz_data):
            u_ans = st.session_state.user_answers.get(idx)
            is_right = u_ans == item["answer"]
            
            exp_label = f"Question {idx+1}: {'✅ Correct' if is_right else '❌ Incorrect'}"
            with st.expander(exp_label, expanded=True):
                st.markdown(f"**Question:** {item['question']}")
                st.markdown(f"**Your Choice:** `{u_ans or 'Unanswered'}`")
                st.markdown(f"**Correct Option:** `{item['answer']}`")
                st.info(f"**Explanation:** {item['explanation']}")

# ==========================================
# TAB 4: STUDY PLANNER & FOCUS TIMER
# ==========================================
with tab4:
    st.markdown("### ⏱️ Pomodoro Focus Timer & Goal Tracker")
    st.caption("Maximize study productivity with timed focus blocks and organized study checklists.")
    
    col_tm1, col_tm2 = st.columns(2)
    
    with col_tm1:
        st.markdown("#### ⌛ Focus Session Timer")
        session_mins = st.slider("Select Session Duration (Minutes)", min_value=5, max_value=60, value=25, step=5)
        
        if "timer_active" not in st.session_state:
            st.session_state.timer_active = False
            
        c1, c2 = st.columns(2)
        with c1:
            if st.button("▶️ Start Session", type="primary", use_container_width=True):
                st.session_state.timer_active = True
        with c2:
            if st.button("⏹️ Reset Timer", use_container_width=True):
                st.session_state.timer_active = False

        timer_box = st.empty()
        if st.session_state.timer_active:
            sec_total = session_mins * 60
            for current_sec in range(sec_total, -1, -1):
                if not st.session_state.timer_active:
                    break
                m, s = divmod(current_sec, 60)
                timer_box.markdown(f"### 🕒 Time Remaining: `{m:02d}:{s:02d}`")
                time.sleep(1)
            if st.session_state.timer_active:
                st.balloons()
                st.success("🎉 Focus session completed! Take a 5-minute break.")
                st.session_state.timer_active = False
        else:
            timer_box.markdown(f"### 🕒 Status: Ready (`{session_mins:02d}:00`)")

    with col_tm2:
        st.markdown("#### 📌 Daily Study Goals")
        new_goal = st.text_input("Add a goal task:", placeholder="e.g. Complete DBMS Module 2, Practice 5 MCQs")
        if "goal_list" not in st.session_state:
            st.session_state.goal_list = [
                {"text": "Review AI Study Buddy Presentation Slides", "done": True},
                {"text": "Complete 25-minute Pomodoro focus block", "done": False}
            ]
            
        if st.button("➕ Add Goal Task") and new_goal.strip():
            st.session_state.goal_list.append({"text": new_goal.strip(), "done": False})
            st.rerun()
            
        st.markdown("---")
        for idx, item in enumerate(st.session_state.goal_list):
            is_done = st.checkbox(item["text"], value=item["done"], key=f"goal_item_{idx}")
            st.session_state.goal_list[idx]["done"] = is_done

# ==========================================
# TAB 5: PROJECT DOCUMENTATION
# ==========================================
with tab5:
    st.markdown("### ℹ️ IBM SkillsBuild & Edunet Foundation Capstone Submission")
    
    st.markdown("""
    #### 🎯 Problem Statement
    Students encounter key obstacles during independent study:
    - Academic concepts are often complex and difficult to grasp without instant guidance.
    - Standard online search engines return lengthy, unstructured, or overwhelming results.
    - Faculty and academic mentors are not available round-the-clock for instant doubt resolution.
    - Lack of unified, interactive tools for instant summarization and self-assessment.

    ---

    #### 💡 Proposed Solution
    **AI Study Buddy Pro** is a responsive web application powered by **Google Gemini 2.5 Flash** and built on top of **Streamlit**.
    It functions as a 24/7 personalized virtual tutor providing:
    1. **Topic Simplification:** Translates complex theories into simple ELI5 analogies.
    2. **Notes & Code Summarization:** Instantly distills lengthy notes, code, or logs into clean key points.
    3. **Interactive MCQ Engine:** Generates real-time quizzes with score tracking and collapsible explanations.
    4. **Productivity Suite:** Built-in Pomodoro focus timer and daily study planner.

    ---

    #### 🛠️ Tech Stack
    - **UI Framework:** Streamlit
    - **Generative AI Model:** Google Gemini 2.5 Flash / Gemini 1.5 Flash (`google-generativeai`)
    - **Configuration Security:** `python-dotenv` for secure environment key loading
    - **Local Host URL:** `http://localhost:8501/`

    ---

    #### 👨‍🎓 Submission Metadata
    - **Student Name:** Kunal Deshmukh
    - **Department:** Information Technology (IT), USICT
    - **AICTE ID:** `STU6885e9f37bd011753606643`
    - **Track:** Artificial Intelligence
    - **GitHub Repository:** [https://github.com/Kunal77744/AI-Study-Buddy](https://github.com/Kunal77744/AI-Study-Buddy)
    """)

# Footer
st.divider()
st.caption("© 2026 AI Study Buddy Capstone | Developed by Kunal Deshmukh for IBM SkillsBuild & Edunet Foundation")
