import streamlit as st
from datetime import datetime
from utils.ibm_api import call_ibm_model
from utils.file_utils import save_chat, load_chat, list_chats, get_unique_chat_id, sanitize_filename
import fitz
from PIL import Image
import pytesseract

MAX_TOTAL_TOKENS = 4096
MAX_OUTPUT_TOKENS = 4096

def estimate_tokens(text):
    return int(len(text) / 4)

def extract_text_from_pdf(file):
    text = ""
    with fitz.open(stream=file.read(), filetype="pdf") as doc:
        for page in doc:
            text += page.get_text()
    return text.strip()

def extract_text_from_image(file):
    try:
        image = Image.open(file)
        return pytesseract.image_to_string(image)
    except Exception:
        return "❌ Image extraction failed try again."

def build_prompt(history, user_input, context=""):
    prompt_parts = []
    available_tokens = MAX_TOTAL_TOKENS - MAX_OUTPUT_TOKENS - estimate_tokens(user_input)

    if context:
        ctx_tokens = estimate_tokens(context)
        if ctx_tokens > available_tokens:
            words = context.split()
            trimmed = []
            for word in words:
                test = " ".join(trimmed + [word])
                if estimate_tokens(test) < available_tokens:
                    trimmed.append(word)
                else:
                    break
            context = " ".join(trimmed)
        prompt_parts.append(context)
        available_tokens -= estimate_tokens(context)

    trimmed_history = []
    for msg in reversed(history):
        if msg["role"] in ("user", "assistant"):
            content = msg["content"]
            tokens = estimate_tokens(content)
            if tokens <= available_tokens:
                trimmed_history.insert(0, content)
                available_tokens -= tokens
            else:
                break
    prompt_parts.extend(trimmed_history)

    user_input = user_input.strip()
    if not user_input.endswith("."):
        user_input += "."
    prompt_parts.append(user_input)

    return "\n\n".join(prompt_parts)

def show():
    st.title("💬 Ask Me")

    if "user" not in st.session_state:
        st.error("🔒 Please login to access this section.")
        return

    if "askme_history" not in st.session_state:
        st.session_state.askme_history = []
        st.session_state.current_chat_id = None

    user = st.session_state["user"]
    st.sidebar.subheader("🗂 Chat Sessions")

    chats = list_chats(user)
    previous_chat = st.session_state.get("previous_chat", "")
    selected_chat = st.sidebar.selectbox("📂 Open Previous", [""] + chats, index=([""] + chats).index(previous_chat) if previous_chat in chats else 0)
    if selected_chat and selected_chat != previous_chat:
        st.session_state["previous_chat"] = selected_chat
        st.session_state.askme_history = load_chat(user, selected_chat)
        st.session_state.current_chat_id = selected_chat
        st.rerun()

    if st.sidebar.button("🆕 New Chat"):
        st.session_state.askme_history = []
        st.session_state.current_chat_id = None
        st.session_state["previous_chat"] = ""
        st.rerun()

    extra_text = ""
    with st.expander("📎 Upload PDF/Image for context (optional)"):
        uploaded_file = st.file_uploader("Upload a PDF or Image", type=["pdf", "png", "jpg", "jpeg"])
        if uploaded_file:
            if uploaded_file.name.endswith(".pdf"):
                extra_text = extract_text_from_pdf(uploaded_file)
            else:
                extra_text = extract_text_from_image(uploaded_file)
            st.success("✅ Context added from uploaded file.")
            if st.checkbox("🔍 Show extracted content"):
                st.text_area("Extracted Context", extra_text, height=200)

    user_input = st.chat_input("Ask me anything...")

    if user_input:
        if not st.session_state["current_chat_id"]:
            with st.spinner("🔤 Generating title..."):
                try:
                    title_prompt = f"Generate a short, meaningful title (max 5 words) summarizing this request: {user_input}"
                    title = call_ibm_model(title_prompt, max_tokens=20, temperature=0.3).strip()
                    title = sanitize_filename(title)
                    chat_id = get_unique_chat_id(user, title)
                    st.session_state["current_chat_id"] = chat_id
                    st.session_state["previous_chat"] = chat_id
                except Exception:
                    fallback = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
                    st.session_state["current_chat_id"] = f"Chat_{fallback}"
                    st.session_state["previous_chat"] = st.session_state["current_chat_id"]

        prompt = build_prompt(st.session_state.askme_history, user_input, context=extra_text)
        if estimate_tokens(prompt) > MAX_TOTAL_TOKENS:
            st.warning("⚠️ Token limit exceeded. Start a new chat or shorten input.")
        else:
            with st.spinner("🤖 Thinking..."):
                response = call_ibm_model(prompt, max_tokens=MAX_OUTPUT_TOKENS, temperature=0.2)
                response = response.strip() if response else "⚠️ No response."

            st.session_state.askme_history.append({"role": "user", "content": user_input})
            st.session_state.askme_history.append({"role": "assistant", "content": response})
            save_chat(user, st.session_state["current_chat_id"], st.session_state.askme_history)

    for msg in st.session_state.askme_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
