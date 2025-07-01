import streamlit as st
from utils.config import ConfigManager
import os

# Streamlit-specific optimizations
@st.cache_resource
def load_resources():
    config = ConfigManager().settings
    chat_engine = ChatEngine(config)
    return chat_engine

# Initialize with config
config = load_config()
st.set_page_config(layout="wide")
chat_engine = load_resources()

st.title("🎓 Crescent University Chatbot")

# Session state initialization
if "memory" not in st.session_state:
    st.session_state.memory = chat_engine.init_memory()
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": config["welcome_message"]}]

# Chat UI
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# API Key Input (Fallback)
if not chat_engine.check_openai_key():
    with st.sidebar:
        api_key = st.text_input("Enter OpenAI API Key", type="password")
        if api_key:
            chat_engine.set_api_key(api_key)

# Processing user input
if user_input := st.chat_input("Ask about admissions, courses, etc..."):
    with st.chat_message("user"):
        st.markdown(user_input)
    
    with st.spinner("Thinking..."):
        response = chat_engine.process_query(user_input)
    
    with st.chat_message("assistant"):
        st.markdown(response)
    
    # Update memory and logs
    st.session_state.messages.extend([
        {"role": "user", "content": user_input},
        {"role": "assistant", "content": response}
    ])
    log_conversation(user_input, response)

with st.sidebar:
    st.subheader("AI Settings")
    use_openai = st.toggle("Use OpenAI GPT", True)
    if st.session_state.get("use_openai") != use_openai:
        st.session_state.use_openai = use_openai
        chat_engine.config["use_openai"] = use_openai
        st.rerun()
