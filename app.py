import streamlit as st
import os
import json
import re
import time
import io
from dotenv import load_dotenv

# Load environment variables quietly
load_dotenv()

# Streamlit Page Configuration
st.set_page_config(
    page_title="AI Study Buddy | IBM SkillsBuild Capstone",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# High-End Modern Custom Styling (CSS)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Plus+Jakarta+Sans:wght@500;600;700;800&display=swap');
    
    * {
        font-family: 'Plus Jakarta Sans', 'Inter', sans-serif;
    }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    .stApp {
        background-color: #F8FAFC;
    }
    
    /* Main Hero Banner */
    .hero-banner {
        background: linear-gradient(135deg, #0F172A 0%, #1E293B 45%, #2563EB 100%);
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
    
    /* Quiz Score Card */
    .quiz-score-card {
        background: linear-gradient(135deg, #059669 0%, #10B981 100%);
        color: white;
        padding: 1.8rem;
        border-radius: 16px;
        text-align: center;
        margin-bottom: 1.8rem;
        box-shadow: 0 10px 15px -3px rgba(16, 185, 129, 0.2);
    }

    .quiz-score-warning {
        background: linear-gradient(135deg, #D97706 0%, #F59E0B 100%);
        color: white;
        padding: 1.8rem;
        border-radius: 16px;
        text-align: center;
        margin-bottom: 1.8rem;
        box-shadow: 0 10px 15px -3px rgba(245, 158, 11, 0.2);
    }
    
    /* Streamlit Tabs */
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

    /* Buttons */
    .stButton>button {
        border-radius: 10px;
        font-weight: 600;
        transition: all 0.2s ease;
    }
    
    .stButton>button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.2);
    }
</style>
""", unsafe_allow_html=True)

# Helper function: PDF Text Extractor
def extract_text_from_file(uploaded_file):
    """
    Extracts plain text from uploaded files including PDF, TXT, MD, PY.
    """
    file_name = uploaded_file.name.lower()
    if file_name.endswith('.pdf'):
        try:
            import pypdf
            reader = pypdf.PdfReader(uploaded_file)
            extracted_text = ""
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    extracted_text += text + "\n"
            return extracted_text.strip()
        except Exception as e:
            return f"❌ Error parsing PDF file: {str(e)}"
    else:
        try:
            return uploaded_file.read().decode("utf-8")
        except Exception as e:
            return f"❌ Error reading file: {str(e)}"

# Helper function: Robust Gemini API Client
def get_gemini_response(prompt, system_instruction=None, api_key=None, model_name="gemini-2.5-flash"):
    """
    Executes request using Gemini API with intelligent fallbacks.
    """
    effective_api_key = api_key or os.getenv("GEMINI_API_KEY", "")
    
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

# Helper function: Robust JSON Quiz Extractor
def extract_json_quiz(raw_text):
    """
    Extracts valid JSON array from raw model response using regex matching.
    """
    clean_text = raw_text.strip()
    if clean_text.startswith("```json"):
        clean_text = clean_text[7:]
    if clean_text.startswith("```"):
        clean_text = clean_text[3:]
    if clean_text.endswith("```"):
        clean_text = clean_text[:-3]
    clean_text = clean_text.strip()
    
    # Try direct parse
    try:
        return json.loads(clean_text)
    except Exception:
        # Regex search for JSON array pattern [...]
        match = re.search(r'\[\s*\{.*\}\s*\]', raw_text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except Exception:
                pass
        raise ValueError("Could not parse JSON array from AI output.")

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
    
    model_choice = st.selectbox(
        "AI Model Mode",
        ["gemini-2.5-flash (Recommended)", "gemini-1.5-flash", "gemini-1.5-pro"],
        index=0
    )

    st.divider()
    
    st.markdown("### 📌 Project Metadata")
    st.markdown("""
    **Project Title:** AI-Powered Study Buddy  
    **Author:** Kunal Deshmukh  
    **Institute:** USICT (IT Department)  
    **Track:** Artificial Intelligence  
    **Capstone Partner:** IBM SkillsBuild & Edunet Foundation
    """)
    
    st.divider()

    # Collapsed Developer Settings
    with st.expander("🔐 Developer Settings", expanded=False):
        custom_key = st.text_input("Custom Gemini API Key Override", type="password", value=os.getenv("GEMINI_API_KEY", ""))
        st.caption("Leave empty to use default environment API configuration.")

# --- HERO BANNER ---
st.markdown("""
<div class="hero-banner">
    <div class="badge-capstone">🎓 IBM SkillsBuild & Edunet Foundation Capstone Project</div>
    <h1>AI-Powered Virtual Study Companion</h1>
    <p>Accelerate your learning journey with instant topic simplification, intelligent document summarization (PDF & Text), automated MCQ quizzes, and interactive focus tools.</p>
</div>
""", unsafe_allow_html=True)

# --- APPLICATION TABS ---
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "💡 Topic Explainer", 
    "📝 Notes & Document Summarizer", 
    "🧠 Interactive MCQ Quiz Generator", 
    "⏱️ Study Planner & Pomodoro Timer", 
    "ℹ️ Architecture & Documentation"
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
            "Enter Topic or Question to Explore", 
            placeholder="e.g. Backpropagation in Neural Networks, Quantum Entanglement, Normalization in DBMS, TCP/IP Model"
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
                
                st.session_state["last_explanation"] = response_text
                st.session_state["last_topic"] = topic_input

    if "last_explanation" in st.session_state:
        st.markdown("---")
        st.markdown("#### 📖 Explanation Output")
        st.markdown(st.session_state["last_explanation"])
        
        st.download_button(
            label="📥 Download Explanation (.md)",
            data=st.session_state["last_explanation"],
            file_name=f"Explanation_{st.session_state.get('last_topic', 'Topic').replace(' ', '_')}.md",
            mime="text/markdown"
        )

# ==========================================
# TAB 2: NOTES & DOCUMENT SUMMARIZER (WITH PDF SUPPORT)
# ==========================================
with tab2:
    st.markdown("### 📝 Notes & Document Summarizer")
    st.caption("Convert raw text, lecture notes, textbooks (PDF), or source code into high-retention summaries.")
    
    input_type = st.radio("Input Source:", ["Text / Code Snippet", "Upload Document File (.pdf, .txt, .md, .py)"], horizontal=True)
    
    raw_content = ""
    if input_type == "Text / Code Snippet":
        raw_content = st.text_area(
            "Paste your notes or code snippet here:",
            height=220,
            placeholder="Paste raw lecture notes, textbook excerpts, or code blocks here..."
        )
    else:
        uploaded_file = st.file_uploader("Upload Notes or PDF Document", type=["pdf", "txt", "md", "py", "json"])
        if uploaded_file is not None:
            with st.spinner("Extracting text from file..."):
                raw_content = extract_text_from_file(uploaded_file)
                if raw_content.startswith("❌"):
                    st.error(raw_content)
                    raw_content = ""
                else:
                    st.success(f"File '{uploaded_file.name}' loaded successfully! ({len(raw_content)} characters extracted)")

    col_s1, col_s2 = st.columns(2)
    with col_s1:
        summary_format = st.selectbox(
            "Summary Output Format",
            ["Structured Bullet Points", "Executive Overview", "Flashcard Q&A Pairs", "Code Analysis & Debugging Tips"]
        )
    with col_s2:
        detail_level = st.select_slider(
            "Summary Detail Level",
            options=["Concise (Key Highlights)", "Standard Balanced Summary", "In-Depth Detailed Analysis"]
        )
        
    if st.button("✨ Summarize Document", type="primary", use_container_width=True):
        if not raw_content.strip():
            st.warning("Please provide notes or upload a file to summarize!")
        else:
            with st.spinner("Processing summary with AI..."):
                prompt = f"""
                Summarize the following text in '{summary_format}' format with detail level '{detail_level}'.
                
                Content:
                \"\"\"
                {raw_content[:15000]}
                \"\"\"
                """
                system_prompt = "You are a professional academic research assistant specializing in notes summarization."
                
                summary_output = get_gemini_response(prompt, system_instruction=system_prompt, api_key=custom_key, model_name=model_choice)
                st.session_state["last_summary"] = summary_output

    if "last_summary" in st.session_state:
        st.markdown("---")
        st.markdown("#### 📋 Generated Summary Output")
        st.markdown(st.session_state["last_summary"])
        
        st.download_button(
            label="📥 Download Summary (.md)",
            data=st.session_state["last_summary"],
            file_name="Study_Notes_Summary.md",
            mime="text/markdown"
        )

# ==========================================
# TAB 3: INTERACTIVE QUIZ GENERATOR
# ==========================================
with tab3:
    st.markdown("### 🧠 Interactive MCQ Quiz Generator")
    st.caption("Generate AI quizzes, test your knowledge, and review real-time scorecards with collapsible explanations.")
    
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
                
                try:
                    quiz_list = extract_json_quiz(raw_res)
                    st.session_state.quiz_data = quiz_list
                    st.session_state.user_answers = {}
                    st.session_state.quiz_submitted = False
                    st.success(f"Quiz on '{quiz_subject}' generated successfully!")
                except Exception as e:
                    st.error("Failed to parse quiz format. Raw AI response:")
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
        card_class = "quiz-score-card" if pct >= 75 else "quiz-score-warning"
        
        st.markdown(f"""
        <div class="{card_class}">
            <h2 style="margin:0; font-size: 2rem;">Quiz Scorecard: {score} / {total} ({pct}%)</h2>
            <p style="margin-top: 0.4rem; font-size: 1.1rem; opacity: 0.95;">
                {'🎉 Outstanding! You have mastered this concept.' if pct >= 75 else '👍 Good effort! Review the explanations below to strengthen your understanding.'}
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        st.progress(pct / 100.0)
        
        st.markdown("#### 🔍 Answer Key & Detailed Explanations:")
        for idx, item in enumerate(st.session_state.quiz_data):
            u_ans = st.session_state.user_answers.get(idx)
            is_right = u_ans == item["answer"]
            
            exp_label = f"Question {idx+1}: {'✅ Correct' if is_right else '❌ Incorrect'}"
            with st.expander(exp_label, expanded=True):
                st.markdown(f"**Question:** {item['question']}")
                st.markdown(f"**Your Answer:** `{u_ans or 'Not Answered'}`")
                st.markdown(f"**Correct Option:** `{item['answer']}`")
                st.info(f"**Explanation:** {item['explanation']}")

# ==========================================
# TAB 4: STUDY PLANNER & POMODORO TIMER
# ==========================================
with tab4:
    st.markdown("### ⏱️ Pomodoro Focus Timer & Task Planner")
    st.caption("Boost study retention with structured focus sessions and daily study goal checklists.")
    
    col_tm1, col_tm2 = st.columns(2)
    
    with col_tm1:
        st.markdown("#### ⌛ Pomodoro Focus Session")
        preset = st.radio("Select Timer Preset:", ["25 min (Focus)", "5 min (Short Break)", "15 min (Long Break)"], horizontal=True)
        
        preset_map = {"25 min (Focus)": 25, "5 min (Short Break)": 5, "15 min (Long Break)": 15}
        session_mins = preset_map[preset]
        
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
                st.success("🎉 Focus session completed! Take a well-deserved break.")
                st.session_state.timer_active = False
        else:
            timer_box.markdown(f"### 🕒 Status: Ready (`{session_mins:02d}:00`)")

    with col_tm2:
        st.markdown("#### 📌 Daily Study Goals Checklist")
        new_goal = st.text_input("Add a study task:", placeholder="e.g. Solve 5 DBMS MCQs, Read Neural Network notes")
        if "goal_list" not in st.session_state:
            st.session_state.goal_list = [
                {"text": "Review AI Study Buddy Capstone Documentation", "done": True},
                {"text": "Complete 25-minute Pomodoro focus block", "done": False}
            ]
            
        col_g1, col_g2 = st.columns([3, 1])
        with col_g1:
            if st.button("➕ Add Task") and new_goal.strip():
                st.session_state.goal_list.append({"text": new_goal.strip(), "done": False})
                st.rerun()
        with col_g2:
            if st.button("🗑️ Clear Done"):
                st.session_state.goal_list = [g for g in st.session_state.goal_list if not g["done"]]
                st.rerun()
            
        st.markdown("---")
        for idx, item in enumerate(st.session_state.goal_list):
            is_done = st.checkbox(item["text"], value=item["done"], key=f"goal_item_{idx}")
            st.session_state.goal_list[idx]["done"] = is_done

# ==========================================
# TAB 5: ARCHITECTURE & DOCUMENTATION
# ==========================================
with tab5:
    st.markdown("### ℹ️ Architecture & Capstone Submission Details")
    
    st.markdown("""
    #### 🎯 Problem Statement & Key Challenges
    Students face significant hurdles during self-study:
    - Academic concepts can be complex and difficult to grasp without on-demand tutoring.
    - Standard search engines yield lengthy, unstructured, or noisy results.
    - Mentors and teachers are not available round-the-clock for instant doubt resolution.
    - Lack of unified, interactive tools for instant note summarization and continuous self-assessment.

    ---

    #### 💡 Proposed Solution & Features
    **AI Study Buddy Pro** is a responsive web application powered by **Google Gemini 2.5 Flash** and built with **Streamlit**.
    - **Topic Simplification:** Translates complex theories into simple ELI5 analogies.
    - **Notes & Document Summarization:** Reads raw text and uploaded PDF notes to output concise key takeaways.
    - **Interactive MCQ Engine:** Generates real-time quizzes with dynamic score tracking and collapsible explanations.
    - **Productivity Suite:** Built-in Pomodoro focus timer and goal tracker.

    ---

    #### 🏗️ System Workflow Architecture
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

    #### 🛠️ Technology Stack
    - **Language:** Python 3.10+
    - **UI Framework:** Streamlit (`streamlit`)
    - **Generative AI Engine:** Google Gemini 2.5 Flash (`google-generativeai`)
    - **PDF Reader Engine:** `pypdf`
    - **Security & Config:** `python-dotenv`

    ---

    #### 👨‍🎓 Project Credits & Submission Info
    - **Developer:** Kunal Deshmukh
    - **Institute:** USICT (Information Technology Dept)
    - **Track:** Artificial Intelligence
    - **Capstone Partner:** IBM SkillsBuild & Edunet Foundation
    - **GitHub Repo:** [https://github.com/Kunal77744/AI-Study-Buddy](https://github.com/Kunal77744/AI-Study-Buddy)
    """)

# Footer
st.divider()
st.caption("© 2026 AI Study Buddy Capstone | Developed by Kunal Deshmukh for IBM SkillsBuild & Edunet Foundation")
