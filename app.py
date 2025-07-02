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

# --- Greeting Generator ---
def generate_greeting() -> str:
    hour = datetime.now().hour
    if 5 <= hour < 12:
        time_greet = random.choice(["Good morning", "Morning"])
    elif 12 <= hour < 17:
        time_greet = random.choice(["Good afternoon", "Afternoon"])
    else:
        time_greet = random.choice(["Good evening", "Evening"])
    return f"{time_greet}! I'm {PERSONALITY['name']}, your Crescent University assistant. How can I help you today?"

# --- Small Talk Handler ---
def handle_small_talk(query: str) -> str:
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
            "I'm a proud creation of Crescent University's AI initiative."
        ],
        "hi": ["Hey there! 😊", "Hi! How can I help you today?"],
        "hello": ["Hello! 👋", "Hi there! Got any questions about the university?"],
        "bye": ["Take care! Feel free to come back anytime.", "Goodbye! All the best."]
    }
    for phrase, replies in responses.items():
        if phrase in query:
            return random.choice(replies)
    return None

# --- Factual Answer Lookup ---
def find_factual_answer(query: str) -> str:
    query = query.lower().strip()

    # 1. Exact Match
    for qa in config["qa_data"]:
        if query == qa["question"].lower().strip():
            return qa["answer"]

    # 2. Keyword Matching
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

# --- Category-Based Fallbacks ---
def get_category_response(category: str) -> str:
    responses = {
        "admiss": [
            "Admissions require 5 credits including Math and English. The cut-off is usually 180+ in UTME.",
            "For admission, you'll need your O'Level results and UTME score. Applications are online at crescent.edu.ng/apply."
        ],
        "fee": [
            "Tuition ranges from ₦500k to ₦800k per session. There's also a ₦50k acceptance fee.",
            "Fees vary by program. Computer Science is ₦750k/session while Mass Comm is ₦650k."
        ],
        "course": [
            "We offer BSc programs in CS, Microbiology, Accounting, and more. Full list on our website!",
            "Popular courses include Computer Science (with AI specialization), Law, and Mass Communication."
        ],
        "hostel": [
            "Yes, Crescent University offers on-campus hostel accommodation for both male and female students.",
            "Our hostels are comfortable, secure, and located within the university premises. Fees depend on the room type."
        ]
    }
    return random.choice(responses.get(category, ["I'll need to check that for you."]))

# --- Response Formulation ---
def formulate_response(query: str, context: dict) -> str:
    if small_talk := handle_small_talk(query):
        return small_talk

    # Add natural thinking pause
    thinking_phrases = [
        "Let me look that up...",
        "Checking my knowledge base...",
        "One moment please...",
        *PERSONALITY["speech_patterns"]["encouraging"]
    ]

    factual = find_factual_answer(query)
    if not factual:
        return "Hmm, I’m not sure about that yet. You can reach out to admissions@crescent.edu.ng or ask me something else!"

    response = random.choice(thinking_phrases) + "\n\n" + factual

    # Add human-like flair
    if random.random() < PERSONALITY["traits"]["enthusiasm"]:
        enhancers = ["By the way", "Did you know", "Oh and"]
        if random.random() < 0.3:
            response += f" {random.choice(enhancers)}, our campus has beautiful gardens!"

    return response

# --- Streamlit Session Management ---
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

# Display message history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("typing"):
            st.caption("...typing")

# Initial Greeting
if st.session_state["first_interaction"]:
    with st.chat_message("assistant"):
        greeting = generate_greeting()
        st.markdown(greeting)
        st.session_state.messages.append({"role": "assistant", "content": greeting})
        st.session_state["first_interaction"] = False

# Chat Input
if prompt := st.chat_input("Type your message..."):
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Simulate response
    with st.chat_message("assistant"):
        with st.empty():
            st.markdown("...")
            time.sleep(random.uniform(0.3, 1.2))

        response = formulate_response(prompt, st.session_state["context"])

        # Gradual typing effect
        display_text = ""
        placeholder = st.empty()
        for char in response:
            display_text += char
            placeholder.markdown(display_text + "▌")
            time.sleep(random.uniform(0.02, 0.08))
        placeholder.markdown(display_text)

    st.session_state.messages.append({
        "role": "assistant",
        "content": response,
        "typing": False
    })

    # Context tracking
    st.session_state["context"]["last_topic"] = prompt.lower()
    if "memory" not in st.session_state:
        st.session_state.memory = {
            "known_topics": set(),
            "user_preferences": {}
        }

    # Prompt for more after multiple interactions
    user_turns = len([m for m in st.session_state.messages if m["role"] == "user"])
    if user_turns > 4:
        follow_up = "\n\nIs there anything else you'd like to know?"
        st.session_state.messages.append({
            "role": "assistant",
            "content": follow_up,
            "typing": False
        })
        st.chat_message("assistant").markdown(follow_up)
