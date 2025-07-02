import streamlit as st
import random
import time
import json
from pathlib import Path
from utils.config import config

# --- Enhanced Dataset Loader ---
def load_qa_data() -> list:
    """Load and validate QA dataset with error handling"""
    try:
        qa_path = Path(__file__).parent / "data" / "qa_dataset.json"
        with open(qa_path, 'r') as f:
            data = json.load(f)
        
        # Validate dataset format
        if not isinstance(data, list):
            st.error("Error: QA dataset must be a list of question-answer pairs")
            return []
        
        required_keys = {"question", "answer"}
        valid_pairs = []
        
        for item in data:
            if not all(key in item for key in required_keys):
                st.warning(f"Skipping invalid QA pair: {item}")
                continue
            valid_pairs.append({
                "question": item["question"].lower().strip(),
                "answer": item["answer"]
            })
        
        return valid_pairs
    
    except Exception as e:
        st.error(f"Failed to load QA data: {str(e)}")
        return []

# --- Initialize with Dataset ---
if "qa_data" not in st.session_state:
    st.session_state.qa_data = load_qa_data()
    if not st.session_state.qa_data:
        st.session_state.qa_data = [  # Fallback data
            {"question": "what are the admission requirements", 
             "answer": "Minimum 5 credits including Math and English"},
            {"question": "how much is the school fees", 
             "answer": "Tuition ranges from ₦500,000 to ₦800,000 per session"}
        ]

# --- Response Generator ---
def get_response(query: str) -> str:
    """Find the best answer from dataset or fallbacks"""
    query = query.lower().strip()
    
    # 1. Check exact matches in dataset
    for qa in st.session_state.qa_data:
        if query == qa["question"]:
            return qa["answer"]
    
    # 2. Check partial matches
    for qa in st.session_state.qa_data:
        if query in qa["question"] or qa["question"] in query:
            return qa["answer"]
    
    # 3. Keyword fallback
    keyword_responses = {
        "admiss": "For admission details, visit crescent.edu.ng/admissions",
        "fee": "See fee breakdown at crescent.edu.ng/fees",
        "course": "Browse courses at crescent.edu.ng/programs"
    }
    
    for keyword, response in keyword_responses.items():
        if keyword in query:
            return response
    
    # 4. Ultimate fallback
    return "I couldn't find that in our records. Please contact info@crescent.edu.ng"

# --- Chat Interface ---
st.title("🎓 Crescent University Chatbot")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append({
        "role": "assistant", 
        "content": "Hello! I'm your Crescent University assistant. Ask me anything!"
    })

# Display chat messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Process user input
if prompt := st.chat_input("Type your question..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Generate response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            # Simulate typing delay
            time.sleep(0.5)
            response = get_response(prompt)
        
        # Display assistant response
        st.markdown(response)
    
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})

# Debug panel
with st.expander("Dataset Status"):
    st.write(f"Loaded {len(st.session_state.qa_data)} QA pairs")
    st.json(st.session_state.qa_data[:3])  # Show first 3 entries
