import streamlit as st
from utils.config import config
from pathlib import Path
import json

# --- Initial Checks ---
def verify_setup():
    """Validate required files exist"""
    errors = []
    
    if not config["qa_data"]:
        errors.append("QA dataset not loaded")
    
    required_dirs = ["data_dir", "log_dir"]
    for d in required_dirs:
        if not Path(config[d]).exists():
            errors.append(f"Directory missing: {config[d]}")
    
    if errors:
        st.error("Setup issues found:\n- " + "\n- ".join(errors))
        st.stop()

verify_setup()

# --- Chat UI ---
st.title("🎓 Crescent University Chatbot")
st.caption("Safe deployment version")

# Session state initialization
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Ask me about admissions, courses, or fees!"}
    ]

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- Processing Pipeline ---
def generate_response(query: str) -> str:
    """Simplified response generator"""
    # 1. Check exact matches
    for qa in config["qa_data"]:
        if query.lower() == qa["question"].lower():
            return qa["answer"]
    
    # 2. Check abbreviations/synonyms
    normalized = query.lower()
    for abbr, full in config["abbreviations"].items():
        normalized = normalized.replace(abbr, full)
    
    # 3. Fallback response
    return "I'm still learning! Please contact admissions for detailed queries."

# --- Main Chat Loop ---
if prompt := st.chat_input("Your question..."):
    # Add user message to history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Generate and display response
    with st.spinner("Thinking..."):
        response = generate_response(prompt)
    
    # Add assistant response
    st.session_state.messages.append({"role": "assistant", "content": response})
    
    # Rerun to update UI
    st.rerun()

# --- Footer ---
st.divider()
st.markdown("""
**Data Files Loaded:**
- Abbreviations: `{}` entries  
- Synonyms: `{}` entries  
- QA Pairs: `{}` questions
""".format(
    len(config["abbreviations"]),
    len(config["synonyms"]),
    len(config["qa_data"])
))
