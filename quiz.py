import streamlit as st
import os, re
from datetime import datetime
from utils.pdf_utils import extract_text_from_pdf
from utils.ibm_api import call_ibm_model
from utils.file_utils import load_json, save_json
def save_quiz_result(user, score, total, topic, difficulty):
    if not user:
        st.error("User not logged in. Cannot save results.")
        return
    path = f"data/quizzes/{user}.json"
    os.makedirs(os.path.dirname(path), exist_ok=True)
    history = load_json(path) if os.path.exists(path) else []
    history.append({
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "topic": topic,
        "difficulty": difficulty,
        "total_questions": total,
        "score": score
    })
    save_json(path, history)
def show():
    if "quiz" not in st.session_state:
        quiz_setup()
    elif st.session_state.get("start_quiz_now"):
        st.session_state.quiz["quiz_started"] = True
        del st.session_state["start_quiz_now"]
        st.rerun()
    elif not st.session_state.quiz.get("quiz_started"):
        quiz_metadata()
    elif st.session_state.quiz.get("quiz_submitted"):
        show_result()
    else:
        quiz_flow()
def quiz_setup():
    st.title("📝 Generate Quiz")
    user = st.session_state.get("user")
    if not user:
        st.warning("Please login to proceed.")
        return
    uploaded_file = st.file_uploader("Upload PDF (optional)", type=["pdf"])
    topic = st.text_input("Or enter a topic manually")
    num_questions = st.number_input("Number of questions", min_value=1, max_value=500, value=5, step=1)
    difficulty = st.selectbox("Difficulty", ["Easy", "Medium", "Hard"])
    if st.button("Generate Quiz"):
        if not uploaded_file and not topic:
            st.warning("Please upload a PDF or enter a topic.")
            return
        content = extract_text_from_pdf(uploaded_file) if uploaded_file else topic
        prompt = f"""
        You are an AI that generates multiple choice questions. Please generate {num_questions} MCQs based on the following topic. Each question should include 4 options and specify the correct answer. Use this exact format:

        Q1. What is the capital of France?
        A) Berlin
        B) Madrid
        C) Paris
        D) Rome
        Answer: C

        Topic: {content}
        Difficulty: {difficulty}
                """
        with st.spinner("⏳ Generating quiz..."):
            result = call_ibm_model(prompt)
        if not result:
            st.error("❌ Model failed to respond.")
            return
        questions = parse_questions(result)
        if not questions:
            st.error("❌ Could not parse questions.")
            return
        st.session_state.quiz = {
            "questions": questions[:num_questions],
            "answers": [None] * num_questions,
            "current_q": 0,
            "topic": topic or "From PDF",
            "difficulty": difficulty,
            "quiz_started": False,
            "quiz_submitted": False,
            "score": 0,
            "confirm_submit": False
        }
        st.rerun()
def quiz_metadata():
    st.markdown("""
    <style>
        [data-testid="stSidebar"] { display: none; }
        [data-testid="collapsedControl"] { display: none; }
    </style>
""", unsafe_allow_html=True)
    quiz = st.session_state.quiz
    st.markdown("""<style>[data-testid="stSidebar"] {display: none;}</style>""", unsafe_allow_html=True)
    st.title("📋 Quiz Overview")
    st.markdown(f"""
**Topic:** `{quiz.get('topic', 'N/A')}`  
**Difficulty:** `{quiz.get('difficulty', 'N/A')}`  
**Questions:** `{len(quiz.get('questions', []))}`  
    """)
    st.markdown("---")
    if st.button("🚀 Start Quiz"):
        st.session_state["start_quiz_now"] = True
        st.rerun()
def quiz_flow():
    st.markdown("""
    <style>
        [data-testid="stSidebar"] { display: none; }
        [data-testid="collapsedControl"] { display: none; }
    </style>
""", unsafe_allow_html=True)
    quiz = st.session_state.quiz
    idx = quiz.get("current_q", 0)
    questions = quiz.get("questions", [])
    if not questions:
        st.error("⚠️ No questions found. Please generate a quiz again.")
        return
    question = questions[idx]
    st.markdown(f"### Q{idx + 1}: {question['question']}")
    selected = st.radio(
        "Choose:",
        question["options"],
        index=question["options"].index(quiz["answers"][idx]) if quiz["answers"][idx] in question["options"] else 0,
        key=f"q_{idx}"
    )
    quiz["answers"][idx] = selected
    col1, col2, col3 = st.columns(3)
    with col1:
        if idx > 0 and st.button("⬅️ Previous"):
            quiz["current_q"] -= 1
            st.rerun()
    with col2:
        st.markdown(f"**Question {idx + 1} / {len(quiz['questions'])}**")
    with col3:
        if idx < len(quiz["questions"]) - 1 and st.button("➡️ Next"):
            quiz["current_q"] += 1
            st.rerun()
    if idx == len(quiz["questions"]) - 1:
        st.markdown("---")
        if not quiz["confirm_submit"]:
            if st.button("✅ Submit Test"):
                quiz["confirm_submit"] = True
                st.rerun()
        else:
            st.warning("Are you sure you want to submit?")
            if st.button("🚨 Confirm Submission"):
                auto_submit()
def auto_submit():
    quiz = st.session_state.quiz
    score = sum(1 for i, ans in enumerate(quiz["answers"]) if ans == quiz["questions"][i]["answer"])
    quiz["score"] = score
    quiz["quiz_submitted"] = True
    user = st.session_state.get("user")
    save_quiz_result(user, score, len(quiz["questions"]), quiz["topic"], quiz["difficulty"])
    st.rerun()
def show_result():
    quiz = st.session_state.quiz
    st.title("📊 Quiz Result")
    st.success(f"✅ You scored **{quiz['score']} / {len(quiz['questions'])}**")
    incorrect = [
        (i, q, a)
        for i, (q, a) in enumerate(zip(quiz["questions"], quiz["answers"]))
        if a != q["answer"]
    ]
    if incorrect:
        st.markdown("### ❌ Incorrect Answers Review:")
        for i, q, a in incorrect:
            st.markdown(f"""
**Q{i+1}: {q['question']}**  
- Your Answer: ❌ `{a}`  
- Correct Answer: ✅ `{q['answer']}`  
            """)
    if st.button("🏠 Return to Home"):
        del st.session_state.quiz
        st.rerun()
def parse_questions(text):
    try:
        text = re.sub(r"\r", "", text)
        text = re.sub(r"\n\s+", "\n", text)
        pattern = re.compile(
            r"Q\d+\.\s*(.*?)\nA\)\s*(.*?)\nB\)\s*(.*?)\nC\)\s*(.*?)\nD\)\s*(.*?)\nAnswer:\s*([A-Da-d])",
            re.MULTILINE | re.DOTALL
        )
        matches = pattern.findall(text)
        if not matches:
            st.warning("⚠️ No matches found in model output.")
            return None
        questions = []
        for m in matches:
            q_text = m[0].strip()
            options = [m[1].strip(), m[2].strip(), m[3].strip(), m[4].strip()]
            correct = {"A": 0, "B": 1, "C": 2, "D": 3}.get(m[5].strip().upper(), None)
            if correct is not None:
                questions.append({
                    "question": q_text,
                    "options": options,
                    "answer": options[correct]
                })
        return questions
    except Exception as e:
        st.error(f"Parser failed: {e}")
        return None
if __name__ == "__main__":
    show()