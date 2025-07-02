import streamlit as st
import random
import time
import json
from pathlib import Path
from difflib import get_close_matches

# --- Simple Sentiment Analysis ---
def analyze_sentiment(text):
    """Basic sentiment analysis without external dependencies"""
    positive_words = {"good", "great", "excellent", "happy", "thanks", "thank you"}
    negative_words = {"bad", "poor", "terrible", "angry", "upset", "frustrated"}
    
    text_lower = text.lower()
    positive = sum(word in text_lower for word in positive_words)
    negative = sum(word in text_lower for word in negative_words)
    
    if positive > negative:
        return "positive"
    elif negative > positive:
        return "negative"
    return "neutral"

# --- Personality System ---
class Personality:
    def __init__(self):
        self.moods = ["happy", "neutral", "helpful"]
        self.current_mood = random.choice(self.moods)
        
    def get_greeting(self):
        hour = time.localtime().tm_hour
        if 5 <= hour < 12:
            time_greet = random.choice(["Morning", "Good morning"])
        elif 12 <= hour < 17:
            time_greet = random.choice(["Afternoon", "Good afternoon"])
        else:
            time_greet = random.choice(["Evening", "Good evening"])
        
        mood_responses = {
            "happy": f"{time_greet}! 😊 How can I help?",
            "neutral": f"{time_greet}. What can I assist with?",
            "helpful": f"{time_greet}! I'm here to help."
        }
        return mood_responses[self.current_mood]
    
    def get_filler(self):
        return random.choice([
            "Let me check...",
            "Interesting question...",
            "One moment please..."
        ])

# --- Main Application ---
def main():
    # Initialize components
    personality = Personality()
    
    # Load QA data
    try:
        qa_path = Path(__file__).parent / "data" / "qa_dataset.json"
        with open(qa_path) as f:
            qa_data = json.load(f)
    except:
        qa_data = [
            {"question": "admission requirements", "answer": "5 credits including Math and English"},
            {"question": "school fees", "answer": "₦500,000 - ₦800,000 per session"}
        ]
    
    # Streamlit UI
    st.title("🎓 Crescent University Assistant")
    
    # Initialize chat
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": personality.get_greeting()}]
    
    # Display messages
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
    
    # Process input
    if prompt := st.chat_input("Ask about admissions, fees, etc..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Generate response
        with st.chat_message("assistant"):
            # Typing indicator
            with st.empty():
                st.markdown("...")
                time.sleep(0.5)
            
            # Get response
            response = ""
            
            # Add filler (50% chance)
            if random.random() < 0.5:
                response += personality.get_filler() + " "
            
            # Find best answer
            query = prompt.lower()
            answer = next(
                (qa["answer"] for qa in qa_data if qa["question"] in query),
                "I'll need to check that for you. Please email info@crescent.edu.ng"
            )
            
            # Add sentiment
            sentiment = analyze_sentiment(prompt)
            if sentiment == "positive":
                answer += random.choice([" 😊", "!"])
            elif sentiment == "negative":
                answer = "I understand your concern. " + answer
            
            response += answer
            
            # Add follow-up (30% chance)
            if random.random() < 0.3:
                response += "\n\nIs there anything else you'd like to know?"
            
            # Display with typing effect
            display_text = ""
            placeholder = st.empty()
            for char in response:
                display_text += char
                placeholder.markdown(display_text + "▌")
                time.sleep(0.05)
            placeholder.markdown(display_text)
        
        # Save response
        st.session_state.messages.append({"role": "assistant", "content": response})

if __name__ == "__main__":
    main()
