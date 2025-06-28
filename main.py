import streamlit as st
from streamlit_cookies_manager import EncryptedCookieManager
from dotenv import load_dotenv
from auth import register_user, login_user
import quiz, askme, resources, dashboard
import os
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
load_dotenv()
st.set_page_config(
    page_title="Smart Teach AI",
    layout="wide",
    initial_sidebar_state="collapsed"
)
cookies = EncryptedCookieManager(
    prefix="eduai_", password="your_secure_cookie_key" 
)
if not cookies.ready():
    st.stop()
if "user" not in st.session_state:
    st.session_state["user"] = cookies.get("user_email") 
if "current_page" not in st.session_state:
    st.session_state["current_page"] = "📊 Dashboard"
if st.session_state["user"] is None:
    st.title("🔐 Welcome to Smart Teach AI")
    action = st.sidebar.radio("Choose Action", ["Login", "Register"])
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    if action == "Login":
        if st.button("Login"):
            if login_user(email, password):
                st.session_state["user"] = email
                cookies["user_email"] =  email
                cookies.save()
                st.session_state["current_page"] = "📊 Dashboard"
                st.rerun()
            else:
                st.error("Invalid credentials.")
    elif action == "Register":
        confirm_password = st.text_input("Confirm Password", type="password")
        if st.button("Register"):
            if password != confirm_password:
                st.warning("Passwords do not match.")
            elif register_user(email, password):
                st.success("Registration successful. Please log in.")
            else:
                st.error("User already exists.")
else:
    name = st.session_state['user'].split('@')[0]
    st.sidebar.title(f"👋 Hello, {name}")
    menu = st.sidebar.radio("Navigate", [
        "📊 Dashboard",
        "📝 Quiz Generator",
        "💬 Ask Me",
        "🔍 Resource Finder"
    ])
    if st.sidebar.button("🚪 Logout"):
        del cookies["user_email"]
        cookies.save()
        st.session_state["user"] = None
        st.session_state["current_page"] = "📊 Dashboard"
        st.rerun()
    if menu:
        st.session_state["current_page"] = menu
    if st.session_state["current_page"] == "📝 Quiz Generator":
        quiz.show()
    elif st.session_state["current_page"] == "💬 Ask Me":
        askme.show()
    elif st.session_state["current_page"] == "🔍 Resource Finder":
        resources.show()
    else:
        dashboard.show()