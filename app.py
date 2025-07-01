import streamlit as st
from utils.config import config
import random
import time

# --- Response Handlers ---
def handle_greeting() -> str:
    """Return context-aware greetings"""
    greetings = [
        "Hello! How can I help you with Crescent University today?",
        "Hi there! Ask me about admissions, courses, or campus life.",
        "Welcome! I'm your Crescent University assistant. What would you like to know?"
    ]
    return random.choice(greetings)

def handle_question(query: str) -> str:
    """Process user questions with multiple fallback layers"""
    query = query.lower().strip()
    
    # 1. Check exact matches
    for qa in config["qa_data"]:
        if query == qa["question"].lower().strip():
            return qa["answer"]
    
    # 2. Check keyword matches
    keyword_responses = {
        "admission": "Admission requires 5 O'Level credits including Math and English. Apply online at crescent.edu.ng",
        "fee": "Undergraduate fees range from ₦500,000 to ₦800,000 per session depending on your program.",
        "hostel": "On-campus hostel fees are ₦150,000 per session. Off-campus options available nearby.",
        "course": "We offer programs in Computer Science, Law, Accounting, and more. See our website for details."
    }
    
    for keyword, response in keyword_responses.items():
        if keyword in query:
            return response
    
    # 3. Final fallback
    return "I'm still learning about that topic. For detailed help, please email info@crescent.edu.ng"

# --- Session Initialization ---
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.first_interaction = True

# --- Chat UI ---
st.title("🎓 Crescent University Assistant")
st.caption("Ask about admissions, fees, courses, or campus life")

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Handle first interaction
if st.session_state.first_interaction:
    with st.chat_message("assistant"):
        greeting = handle_greeting()
        st.markdown(greeting)
        st.session_state.messages.append({"role": "assistant", "content": greeting})
        st.session_state.first_interaction = False

# Process user input
if prompt := st.chat_input("Type your question here..."):
    # Add user message to history
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Generate and display response
    with st.chat_message("assistant"):
        if any(greet in prompt.lower() for greet in ["hi", "hello", "hey"]):
            response = handle_greeting()
        else:
            with st.spinner("Finding the best answer..."):
                time.sleep(0.5)  # Simulate processing
                response = handle_question(prompt)
        
        st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})
    
    # Ensure UI updates
    st.rerun()

# Debug panel (visible only during development)
if st.secrets.get("DEBUG_MODE", False):
    with st.expander("Debug Info"):
        st.json({
            "qa_pairs_loaded": len(config["qa_data"]),
            "last_query": prompt if 'prompt' in locals() else None,
            "session_messages": st.session_state.messages
        })
