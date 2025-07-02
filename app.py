import streamlit as st
import random
import time
from datetime import datetime
from utils.config import config

# --- Conversation Personality Settings ---
PERSONALITY = {
    "name": "CrescentBot",
    "mood": "friendly",
    "traits": {
        "enthusiasm": 0.8,
        "patience": 0.9,
        "humor": 0.4
    },
    "speech_patterns": {
        "casual": ["Cool", "Got it", "Alright"],
        "empathetic": ["I understand", "That's interesting", "I see"],
        "encouraging": ["Great question!", "I'd be happy to help", "Let me check"]
    }
}

# --- Enhanced Response Handlers ---
def generate_greeting() -> str:
    """Time-aware personalized greetings"""
    hour = datetime.now().hour
    if 5 <= hour < 12:
        time_greet = random.choice(["Good morning", "Morning"])
    elif 12 <= hour < 17:
        time_greet = random.choice(["Good afternoon", "Afternoon"])
    else:
        time_greet = random.choice(["Good evening", "Evening"])
    
    return f"{time_greet}! I'm {PERSONALITY['name']}, your Crescent University assistant. How can I help you today?"

def handle_small_talk(query: str) -> str:
    """Natural conversation responses"""
    query = query.lower()
    
    responses = {
        "how are you": [
            "I'm doing great! Ready to help you with university matters.",
            "All systems go! What can I do for you today?",
            "Feeling excited to help students like you!"
        ],
        "thank you": [
            "You're very welcome! 😊",
            "My pleasure! Don't hesitate to ask more.",
            "Glad I could help! *virtual high five*"
        ],
        "who made you": [
            "I was created by the university's tech team to assist students like you!",
            "The Computer Science department gave me digital life!",
            "I'm a proud creation of Crescent University's AI initiative"
        ]
    }
    
    for phrase, replies in responses.items():
        if phrase in query:
            return random.choice(replies)
    return None

def formulate_response(query: str, context: dict) -> str:
    """Human-like response formulation"""
    # 1. Check for small talk
    if small_talk_response := handle_small_talk(query):
        return small_talk_response
    
    # 2. Add thinking phrases
    thinking_phrases = [
        "Let me look that up...",
        "Checking my knowledge base...",
        "One moment please...",
        *PERSONALITY["speech_patterns"]["encouraging"]
    ]
    
    # 3. Find factual response
    response = find_factual_answer(query) or \
               "I'm still learning about that. For official information, please contact admissions@crescent.edu.ng"
    
    # 4. Add human touches
    if random.random() < PERSONALITY["traits"]["enthusiasm"]:
        enhancers = ["By the way", "Did you know", "Oh and"]
        if random.random() < 0.3:
            response += f" {random.choice(enhancers)}, our campus has beautiful gardens!"
    
    return response

def find_factual_answer(query: str) -> str:
    """Multi-layered knowledge lookup"""
    query = query.lower().strip()
    
    # 1. Exact match
    for qa in config["qa_data"]:
        if query == qa["question"].lower().strip():
            return qa["answer"]
    
    # 2. Keyword match
    keyword_map = {
        "admiss": ["admission", "apply", "requirement"],
        "fee": ["fee", "tuition", "payment"],
        "course": ["course", "program", "curriculum"],
        "hostel": ["hostel", "accommodation", "housing"]
    }
    
    for category, keywords in keyword_map.items():
        if any(kw in query for kw in keywords):
            return get_category_response(category)
    
    return None

def get_category_response(category: str) -> str:
    """Contextual responses with variations"""
    responses = {
        "admiss": [
            "Admissions require 5 credits including Math and English. The cut-off is usually 180+ in UTME.",
            "For admission, you'll need your O'Level results and UTME score. Applications are online at crescent.edu.ng/apply"
        ],
        "fee": [
            "Tuition ranges from ₦500k to ₦800k per session. There's also a ₦50k acceptance fee.",
            "Fees vary by program. Computer Science is ₦750k/session while Mass Comm is ₦650k."
        ],
        "course": [
            "We offer BSc programs in CS, Microbiology, Accounting, and more. Full list on our website!",
            "Popular courses include Computer Science (with AI specialization), Law, and Mass Communication."
        ]
    }
    return random.choice(responses.get(category, ["I'll need to check that for you."]))

# --- Session Management ---
if "messages" not in st.session_state:
    st.session_state.update({
        "messages": [],
        "first_interaction": True,
        "user_name": None,
        "context": {"last_topic": None}
    })

# --- UI Setup ---
st.title(f"🤖 {PERSONALITY['name']}")
st.caption("Your human-like university assistant")

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("typing"):
            st.caption("...typing")

# First interaction greeting
if st.session_state["first_interaction"]:
    with st.chat_message("assistant"):
        greeting = generate_greeting()
        st.markdown(greeting)
        st.session_state.messages.append({"role": "assistant", "content": greeting})
        st.session_state["first_interaction"] = False

# Process user input
if prompt := st.chat_input("Type your message..."):
    # Store user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Generate response
    with st.chat_message("assistant"):
        # Simulate typing
        with st.empty():
            st.markdown("...")
            time.sleep(random.uniform(0.3, 1.2))
        
        # Get and display response
        response = formulate_response(prompt, st.session_state["context"])
        
        # Type out response gradually
        display_text = ""
        placeholder = st.empty()
        for char in response:
            display_text += char
            placeholder.markdown(display_text + "▌")
            time.sleep(random.uniform(0.02, 0.08))
        placeholder.markdown(display_text)
    
    # Store assistant response
    st.session_state.messages.append({
        "role": "assistant",
        "content": response,
        "typing": False
    })
    
    # Update context
    st.session_state["context"]["last_topic"] = prompt.lower()
