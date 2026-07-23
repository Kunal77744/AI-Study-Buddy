import streamlit as st
import os
import json
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="AI-Powered Study Buddy",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    .main-header {
        background: linear-gradient(135deg, #1E3A8A 0%, #3B82F6 50%, #1D4ED8 100%);
        padding: 2.5rem;
        border-radius: 16px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 10px 25px -5px rgba(59, 130, 246, 0.3);
    }
    
    .main-header h1 {
        font-size: 2.6rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        color: #FFFFFF !important;
    }
    
    .main-header p {
        font-size: 1.1rem;
        opacity: 0.95;
        margin-bottom: 0;
    }
    
    .badge-capstone {
        display: inline-block;
        background-color: rgba(255, 255, 255, 0.2);
        backdrop-filter: blur(8px);
        padding: 0.35rem 0.9rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        margin-bottom: 1rem;
        border: 1px solid rgba(255, 255, 255, 0.3);
    }
    
    .card-box {
        background: #FFFFFF;
        padding: 1.8rem;
        border-radius: 14px;
        border: 1px solid #E2E8F0;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.03);
        margin-bottom: 1.5rem;
    }
    
    .quiz-score-card {
        background: linear-gradient(135deg, #059669 0%, #10B981 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 12px;
        text-align: center;
        margin-bottom: 1.5rem;
    }

    .stButton>button {
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.2s ease-in-out;
    }
    
    .stButton>button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    }
</style>
""", unsafe_allow_html=True)

# Helper function to initialize Gemini API Client
def get_gemini_response(prompt, system_instruction=None, api_key=None, model_name="gemini-2.5-flash"):
    """
    Calls Google Gemini API using google-generativeai or REST fallback.
    """
    effective_api_key = api_key or os.getenv("GEMINI_API_KEY")
    if not effective_api_key:
        return "⚠️ **API Key Missing**: Please provide your Google Gemini API Key in the sidebar or set `GEMINI_API_KEY` in `.env` file."
    
    try:
        import google.generativeai as genai
        genai.configure(api_key=effective_api_key)
        
        # Select appropriate model name
        target_model = "gemini-1.5-flash" if "1.5" in model_name else "gemini-2.5-flash"
        
        try:
            model = genai.GenerativeModel(target_model, system_instruction=system_instruction)
            response = model.generate_content(prompt)
            return response.text
        except Exception:
            # Fallback to general model if target_model fails
            model = genai.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content(prompt)
            return response.text

    except ImportError:
        # Fallback to direct REST API if package is missing
        import requests
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={effective_api_key}"
        payload = {
            "contents": [{"parts": [{"text": (system_instruction + "\n\n" if system_instruction else "") + prompt}]}]
        }
        res = requests.post(url, json=payload, headers={"Content-Type": "application/json"})
        if res.status_code == 200:
            return res.json()["candidates"][0]["content"]["parts"][0]["text"]
        else:
            return f"❌ **API Error ({res.status_code})**: {res.text}"
    except Exception as e:
        return f"❌ **Error generating response**: {str(e)}"

# --- SIDEBAR CONFIGURATION ---
with st.sidebar:
    st.image("https://img.icons8.com/illustrations/120/graduation-cap.png", width=70)
    st.title("🎓 Study Buddy Settings")
    
    # API Key Input
    env_key = os.getenv("GEMINI_API_KEY", "")
    api_key = st.text_input(
        "🔑 Gemini API Key",
        value=env_key,
        type="password",
        help="Get your free API Key from Google AI Studio (ai.google.dev)"
    )
    
    # Model Selection
    model_choice = st.selectbox(
        "🤖 AI Model",
        ["gemini-2.5-flash", "gemini-1.5-flash", "gemini-1.5-pro"],
        index=0
    )
    
    st.divider()
    
    # Project Capstone Metadata
    st.markdown("### 📌 Project Info")
    st.info("""
    **Project Title:** AI-Powered Study Buddy  
    **Author:** Kunal Deshmukh  
    **Department:** IT, USICT  
    **AICTE ID:** STU6885e9f37bd011753606643  
    **Submitted To:** IBM SkillsBuild & Edunet Foundation
    """)
    
    st.caption("Powered by Google Gemini 2.5 Flash & Streamlit")

# --- MAIN HEADER ---
st.markdown("""
<div class="main-header">
    <div class="badge-capstone">🎓 IBM SkillsBuild & Edunet Foundation Capstone Project</div>
    <h1>AI-Powered Study Buddy</h1>
    <p>Your 24/7 Virtual Companion for Simplifying Concepts, Summarizing Notes & Interactive Self-Assessment</p>
</div>
""", unsafe_allow_html=True)

# --- NAVIGATION TABS ---
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "💡 Explain a Topic", 
    "📝 Summarize Notes & Code", 
    "🧠 Interactive Quiz", 
    "⏱️ Study Planner & Timer", 
    "ℹ️ Project Overview"
])

# ==========================================
# TAB 1: EXPLAIN A TOPIC (ELI5 & ANALOGIES)
# ==========================================
with tab1:
    st.header("💡 Explain Any Academic Topic")
    st.write("Understand complex subjects using simplified explanations, real-world analogies, and key takeaways.")
    
    col1, col2 = st.columns([2, 1])
    with col1:
        topic_input = st.text_input("Enter Topic or Question", placeholder="e.g. Backpropagation in Neural Networks, Quantum Entanglement, TCP 3-Way Handshake")
    with col2:
        explanation_level = st.selectbox(
            "Target Explanation Level",
            ["ELI5 (Explain Like I'm 10)", "High School Student", "Undergrad / Technical Detail", "Analogy-Driven"],
            index=0
        )
    
    learning_style = st.multiselect(
        "Include in Explanation:",
        ["Real-World Analogy", "Step-by-Step Breakdown", "Key Formulae / Code", "Common Misconceptions", "Self-Test Question"],
        default=["Real-World Analogy", "Step-by-Step Breakdown", "Self-Test Question"]
    )
    
    if st.button("🚀 Explain Topic", type="primary", use_container_width=True):
        if not topic_input.strip():
            st.warning("Please enter a topic to explain!")
        else:
            with st.spinner("AI Study Buddy is analyzing the topic and preparing an intuitive explanation..."):
                prompt = f"""
                Explain the topic: '{topic_input}' for an audience level: '{explanation_level}'.
                Please ensure you include the following elements: {', '.join(learning_style)}.
                Format the response with Markdown headers, bullet points, and bold text for easy reading.
                """
                system_prompt = "You are an expert, encouraging AI Tutor designed to make any difficult concept crystal clear for students."
                
                result = get_gemini_response(prompt, system_instruction=system_prompt, api_key=api_key, model_name=model_choice)
                
                st.markdown("---")
                st.markdown(result)
                st.toast("Explanation generated successfully!", icon="✨")

# ==========================================
# TAB 2: SUMMARIZE NOTES & CODE
# ==========================================
with tab2:
    st.header("📝 Notes & Code Summarizer")
    st.write("Paste your lengthy lecture notes, textbook chapters, or programming code to get concise summaries.")
    
    input_method = st.radio("Select Input Method:", ["Paste Text / Code", "Upload File (.txt, .md)"], horizontal=True)
    
    content_to_summarize = ""
    if input_method == "Paste Text / Code":
        content_to_summarize = st.text_area(
            "Paste your notes, essay, or code snippet here:",
            height=220,
            placeholder="Paste raw text, lecture notes, or code blocks here..."
        )
    else:
        uploaded_file = st.file_uploader("Upload Notes File", type=["txt", "md", "py", "json"])
        if uploaded_file is not None:
            content_to_summarize = uploaded_file.read().decode("utf-8")
            st.success(f"File '{uploaded_file.name}' loaded successfully! ({len(content_to_summarize)} characters)")
    
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        summary_type = st.selectbox(
            "Summary Output Format",
            ["Bullet Point Key Takeaways", "Executive Summary", "Flashcards Format", "Code Explanation & Error Debugger"]
        )
    with col_s2:
        summary_length = st.select_slider(
            "Summary Detail Level",
            options=["Ultra-Short (3-5 Bullets)", "Balanced Summary", "Comprehensive Deep-Dive"]
        )
    
    if st.button("✨ Generate Summary", type="primary", use_container_width=True):
        if not content_to_summarize.strip():
            st.warning("Please provide notes or content to summarize!")
        else:
            with st.spinner("Summarizing notes..."):
                prompt = f"""
                Summarize the following content in '{summary_type}' format with detail level '{summary_length}'.
                
                Content:
                \"\"\"
                {content_to_summarize}
                \"\"\"
                """
                system_prompt = "You are a top-tier academic research assistant specializing in creating structured, high-retention notes."
                
                summary_result = get_gemini_response(prompt, system_instruction=system_prompt, api_key=api_key, model_name=model_choice)
                
                st.markdown("---")
                st.subheader("📋 Output Summary")
                st.markdown(summary_result)

# ==========================================
# TAB 3: INTERACTIVE QUIZ GENERATOR
# ==========================================
with tab3:
    st.header("🧠 Interactive Quiz Generator")
    st.write("Test your knowledge with custom AI-generated multiple-choice quizzes!")
    
    # Initialize session state for quiz
    if "quiz_data" not in st.session_state:
        st.session_state.quiz_data = None
    if "user_answers" not in st.session_state:
        st.session_state.user_answers = {}
    if "quiz_submitted" not in st.session_state:
        st.session_state.quiz_submitted = False
    
    col_q1, col_q2, col_q3 = st.columns([2, 1, 1])
    with col_q1:
        quiz_topic = st.text_input("Quiz Topic / Subject", placeholder="e.g. Data Structures, Machine Learning, World History")
    with col_q2:
        num_questions = st.number_input("Number of Questions", min_value=1, max_value=10, value=4)
    with col_q3:
        quiz_difficulty = st.selectbox("Difficulty", ["Easy", "Medium", "Hard"])
        
    if st.button("🎯 Generate New Quiz", type="primary"):
        if not quiz_topic.strip():
            st.warning("Please enter a topic for the quiz!")
        else:
            with st.spinner(f"Generating {num_questions} {quiz_difficulty} MCQs on '{quiz_topic}'..."):
                json_format_prompt = """
                Return ONLY a valid JSON array of question objects without markdown block tags. Each object must have:
                {
                    "id": 1,
                    "question": "Question text?",
                    "options": ["Option A", "Option B", "Option C", "Option D"],
                    "answer": "Option A",
                    "explanation": "Detailed explanation of why Option A is correct."
                }
                """
                prompt = f"Generate {num_questions} multiple-choice questions on '{quiz_topic}' at '{quiz_difficulty}' level. {json_format_prompt}"
                system_prompt = "You are an automated quiz generation engine. Output ONLY valid raw JSON array."
                
                raw_response = get_gemini_response(prompt, system_instruction=system_prompt, api_key=api_key, model_name=model_choice)
                
                # Cleanup potential backticks in output
                clean_json = raw_response.strip()
                if clean_json.startswith("```json"):
                    clean_json = clean_json[7:]
                if clean_json.startswith("```"):
                    clean_json = clean_json[3:]
                if clean_json.endswith("```"):
                    clean_json = clean_json[:-3]
                clean_json = clean_json.strip()
                
                try:
                    quiz_list = json.loads(clean_json)
                    st.session_state.quiz_data = quiz_list
                    st.session_state.user_answers = {}
                    st.session_state.quiz_submitted = False
                    st.success("Quiz generated! Answer the questions below.")
                except Exception as e:
                    st.error("Failed to parse JSON response for quiz. Raw output:")
                    st.code(raw_response)

    # Display Quiz Form if available
    if st.session_state.quiz_data is not None:
        st.markdown("---")
        st.subheader("📝 Answer the Questions:")
        
        with st.form(key="quiz_form"):
            for idx, q in enumerate(st.session_state.quiz_data):
                st.markdown(f"**Q{idx+1}. {q['question']}**")
                choice = st.radio(
                    f"Select option for Q{idx+1}:",
                    options=q["options"],
                    key=f"q_{idx}",
                    index=None
                )
                st.session_state.user_answers[idx] = choice
                st.markdown("")
            
            submit_quiz = st.form_submit_button("🏆 Submit Answers & View Results", type="primary", use_container_width=True)
            
            if submit_quiz:
                st.session_state.quiz_submitted = True

    # Show Quiz Score and Explanations
    if st.session_state.get("quiz_submitted", False) and st.session_state.quiz_data:
        correct_count = 0
        total_questions = len(st.session_state.quiz_data)
        
        for idx, q in enumerate(st.session_state.quiz_data):
            user_ans = st.session_state.user_answers.get(idx)
            if user_ans == q["answer"]:
                correct_count += 1
                
        score_percent = int((correct_count / total_questions) * 100)
        
        st.markdown(f"""
        <div class="quiz-score-card">
            <h2>Quiz Results: {correct_count} / {total_questions} ({score_percent}%)</h2>
            <p>{'🎉 Excellent performance!' if score_percent >= 75 else '👍 Good effort! Review the explanations below.'}</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.subheader("🔍 Review & Explanations:")
        for idx, q in enumerate(st.session_state.quiz_data):
            user_ans = st.session_state.user_answers.get(idx)
            is_correct = user_ans == q["answer"]
            
            exp_title = f"Q{idx+1}: {q['question']} - {'✅ Correct' if is_correct else '❌ Incorrect'}"
            with st.expander(exp_title, expanded=True):
                st.write(f"**Your Choice:** {user_ans or 'Not Answered'}")
                st.write(f"**Correct Answer:** {q['answer']}")
                st.info(f"**Explanation:** {q['explanation']}")

# ==========================================
# TAB 4: STUDY PLANNER & POMODORO TIMER
# ==========================================
with tab4:
    st.header("⏱️ Study Planner & Pomodoro Timer")
    st.write("Stay focused and boost productivity with a built-in study timer and task checklist.")
    
    col_t1, col_t2 = st.columns([1, 1])
    
    with col_t1:
        st.subheader("⏳ Pomodoro Timer")
        timer_minutes = st.slider("Select Focus Session (Minutes)", min_value=5, max_value=60, value=25, step=5)
        
        if "timer_running" not in st.session_state:
            st.session_state.timer_running = False
        
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("▶️ Start Focus Session", type="primary", use_container_width=True):
                st.session_state.timer_running = True
        with col_btn2:
            if st.button("⏹️ Reset Timer", use_container_width=True):
                st.session_state.timer_running = False
        
        timer_placeholder = st.empty()
        if st.session_state.timer_running:
            total_seconds = timer_minutes * 60
            for sec in range(total_seconds, -1, -1):
                if not st.session_state.timer_running:
                    break
                mins, secs = divmod(sec, 60)
                timer_placeholder.markdown(f"### 🕒 Time Remaining: `{mins:02d}:{secs:02d}`")
                time.sleep(1)
            if st.session_state.timer_running:
                st.balloons()
                st.success("🎉 Focus Session Completed! Take a 5-minute break.")
                st.session_state.timer_running = False
        else:
            timer_placeholder.markdown(f"### 🕒 Ready: `{timer_minutes:02d}:00`")
            
    with col_t2:
        st.subheader("📌 Today's Study Goals")
        new_task = st.text_input("Add a new task:", placeholder="e.g. Complete Machine Learning Quiz, Review Chapter 3")
        if "tasks" not in st.session_state:
            st.session_state.tasks = [
                {"task": "Review AI-Powered Study Buddy Presentation", "done": True},
                {"task": "Complete 25-min Focus Session", "done": False}
            ]
            
        if st.button("➕ Add Task") and new_task.strip():
            st.session_state.tasks.append({"task": new_task.strip(), "done": False})
            st.rerun()
            
        st.write("---")
        for i, t in enumerate(st.session_state.tasks):
            checked = st.checkbox(t["task"], value=t["done"], key=f"task_{i}")
            st.session_state.tasks[i]["done"] = checked

# ==========================================
# TAB 5: PROJECT OVERVIEW & CAPSTONE INFO
# ==========================================
with tab5:
    st.header("ℹ️ Capstone Project Submission Details")
    
    st.markdown("""
    ### 🎯 Problem Statement
    Students often face difficulties during self-study hours:
    - Academic concepts can be overwhelming or hard to grasp without immediate help.
    - Online search engine results are frequently lengthy, unstructured, or irrelevant.
    - Mentors and teachers are not available 24/7 for instant doubt resolution.
    - Lack of unified, interactive tools for instant summarization and self-assessment.

    ---

    ### 💡 Proposed Solution
    **AI Study Buddy Pro** is a responsive web application built using **Streamlit** and powered by **Google Gemini 2.5 Flash**. 
    It functions as an all-in-one virtual companion providing:
    1. **Topic Simplification:** Breaks down complex subjects using ELI5 (Explain Like I'm 10) analogies.
    2. **Notes & Code Summarization:** Instantly converts lecture notes, code blocks, or error logs into concise bullet points.
    3. **Interactive MCQ Quizzes:** Generates customized quizzes with real-time score tracking and collapsible explanations.
    4. **Productivity Suite:** Integrated Pomodoro timer and study goal planner.

    ---

    ### 🛠️ Technology Stack & Libraries
    - **Language:** Python 3.10+
    - **User Interface Framework:** Streamlit
    - **Generative AI Model:** Google Gemini 2.5 Flash / Gemini 1.5 Flash (`google-generativeai`)
    - **Environment Security:** `python-dotenv` for local API key management
    
    ---

    ### 👨‍🎓 Project Credits & Submission Info
    - **Developer:** Kunal Deshmukh
    - **Department:** Information Technology (IT), USICT
    - **AICTE ID:** `STU6885e9f37bd011753606643`
    - **Track:** Artificial Intelligence
    - **Capstone Partner:** IBM SkillsBuild & Edunet Foundation
    """)

# Footer
st.divider()
st.caption("© 2026 AI Study Buddy Capstone Project | Developed by Kunal Deshmukh for IBM SkillsBuild & Edunet Foundation")
