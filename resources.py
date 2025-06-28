import streamlit as st
from utils.file_utils import save_json, load_json
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from utils.ibm_api import call_ibm_model
import os
HISTORY_DIR = "history_resources"
os.makedirs(HISTORY_DIR, exist_ok=True)
def web_search(query, top_n=5):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        resp = requests.get(f"https://duckduckgo.com/html/?q={query}", headers=headers)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        links = []
        for a in soup.select("a.result__a")[:top_n]:
            links.append({
                "title": a.get_text(strip=True),
                "url": a.get("href")
            })
        return links
    except Exception as e:
        return []
def get_history_path(user):
    return os.path.join(HISTORY_DIR, f"{user}_resources.json")
def load_history(user):
    path = get_history_path(user)
    return load_json(path) if os.path.exists(path) else []
def save_history(user, history):
    path = get_history_path(user)
    save_json(path, history)
def show():
    st.title("🔍 Resource Finder")
    if "user" not in st.session_state:
        st.error("🔒 Please log in to use this feature.")
        return
    user = st.session_state["user"]
    history = load_history(user)
    topic = st.text_input("Enter a topic to search", key="resource_input")
    if st.button("Search"):
        if not topic.strip():
            st.warning("⚠️ Please enter a valid topic.")
            return
        with st.spinner("🔄 Searching..."):
            try:
                ai_prompt = f"List 5 high-quality online resources to learn about: {topic}."
                ai_response = call_ibm_model(ai_prompt, max_tokens=200, temperature=0.2)
            except Exception as e:
                ai_response = ""
                st.error(f"AI Error: {e}")
            links = web_search(f"{topic} tutorial")
        st.subheader("🧠 AI Suggestions")
        st.markdown(ai_response if ai_response else "_No AI response._")
        entry = {
            "topic": topic,
            "time": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "ai_response": ai_response.strip(),
        }
        history.append(entry)
        save_history(user, history)
    if history:
        st.markdown("---")
        st.subheader("🕒 Your Past Searches")
        for entry in reversed(history[-5:]):
            with st.expander(f"{entry['topic']} ({entry['time']})"):
                st.markdown("**🧠 AI Suggestion:**")
                st.markdown(entry.get("ai_response", "_No AI response saved._"))