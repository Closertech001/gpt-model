import streamlit as st
from utils.config import config
from pathlib import Path
import json

# --- Setup Validation ---
def validate_qa_data(data: list) -> bool:
    if not data:
        st.error("No QA data loaded! Using fallback mode")
        return False
    
    required_keys = {"question", "answer"}
    for i, item in enumerate(data, 1):
        if not isinstance(item, dict):
            st.error(f"Item {i} is not a dictionary")
            return False
        if not required_keys.issubset(item.keys()):
            st.error(f"Item {i} missing required keys")
            return False
    
    return True

if not validate_qa_data(config["qa_data"]):
    config["qa_data"] = [  # Fallback data
        {"question": "What are the admission requirements?", "answer": "Minimum 5 credits including Math and English"}
    ]

# --- Chat Interface ---
st.title("🎓 Crescent University Chatbot")

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "How can I help with Crescent University?"}
    ]

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- Response Generation ---
def get_response(query: str) -> str:
    query = query.lower()
    
    # 1. Check exact matches
    for qa in config["qa_data"]:
        if query == qa["question"].lower():
            return qa["answer"]
    
    # 2. Check keywords
    if "admission" in query:
        return "Admissions require 5 O'Level credits. Apply via our website."
    if "fee" in query:
        return "Tuition ranges from ₦500,000 to ₦800,000 per session."
    
    return "I don't have that information. Please contact admissions@crescent.edu.ng"

if prompt := st.chat_input("Ask about admissions, fees, etc..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.spinner("Searching knowledge base..."):
        response = get_response(prompt)
    
    st.session_state.messages.append({"role": "assistant", "content": response})
    st.rerun()

# --- Debug Panel ---
with st.expander("Debug Info"):
    st.json({
        "loaded_qa_pairs": len(config["qa_data"]),
        "abbreviations": len(config["abbreviations"]),
        "synonyms": len(config["synonyms"])
    })
