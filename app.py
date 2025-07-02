import streamlit as st
import random
import time
import json
from pathlib import Path
from textblob import TextBlob
from difflib import get_close_matches

# --- Personality System ---
class Personality:
    def __init__(self):
        self.traits = {
            "friendly": 0.9,
            "professional": 0.7,
            "humorous": 0.4
        }
        self.mood = self._detect_mood()
        
    def _detect_mood(self):
        """Simulate mood variations"""
        moods = ["happy", "neutral", "energetic"]
        return random.choice(moods)
    
    def get_greeting(self):
        """Time-aware personalized greetings"""
        hour = time.localtime().tm_hour
        if 5 <= hour < 12:
            base = random.choice(["Morning", "Good morning"])
        elif 12 <= hour < 17:
            base = random.choice(["Afternoon", "Good afternoon"])
        else:
            base = random.choice(["Evening", "Good evening"])
        
        styles = {
            "happy": f"{base}! 😊 How can I brighten your day?",
            "neutral": f"{base}. How may I help you?",
            "energetic": f"{base}!! Ready to tackle your questions! 💪"
        }
        return styles[self.mood]
    
    def get_filler(self):
        """Conversational fillers"""
        return random.choice([
            "Let me think about that...",
            "Hmm, interesting question...",
            "Checking my knowledge base..."
        ])

# --- Conversation Memory ---
class ConversationMemory:
    def __init__(self):
        self.history = []
        self.context = {
            "last_topic": None,
            "user_interests": set(),
            "user_name": None
        }
    
    def update(self, query, response):
        self.history.append((query, response))
        
        # Detect name
        if "my name is" in query.lower():
            self.context["user_name"] = query.split("my name is")[-1].strip()
        
        # Track interests
        topics = ["admission", "fee", "course", "hostel", "scholarship"]
        for topic in topics:
            if topic in query.lower():
                self.context["user_interests"].add(topic)
        
        self.context["last_topic"] = query.lower()
    
    def get_personalization(self):
        """Add contextual references"""
        if not self.context["user_name"]:
            return ""
        
        # Use name occasionally (30% chance)
        if random.random() < 0.3:
            return f" {self.context['user_name']}"
        return ""

# --- Natural Language Processing ---
class NLPEngine:
    def analyze_sentiment(self, text):
        analysis = TextBlob(text)
        if analysis.sentiment.polarity > 0.3:
            return "positive"
        elif analysis.sentiment.polarity < -0.3:
            return "negative"
        return "neutral"
    
    def correct_typos(self, query, known_questions):
        matches = get_close_matches(query, known_questions, n=1, cutoff=0.6)
        return matches[0] if matches else query

# --- Knowledge Base ---
class KnowledgeBase:
    def __init__(self):
        self.qa_data = self._load_qa_data()
    
    def _load_qa_data(self):
        try:
            qa_path = Path(__file__).parent / "data" / "qa_dataset.json"
            with open(qa_path, 'r') as f:
                data = json.load(f)
            
            validated = []
            for item in data:
                if isinstance(item, dict) and "question" in item and "answer" in item:
                    validated.append({
                        "question": item["question"].lower().strip(),
                        "answer": item["answer"]
                    })
            return validated
        except Exception:
            return [
                {"question": "what are the admission requirements", 
                 "answer": "Minimum 5 credits including Math and English"},
                {"question": "how much is the school fees", 
                 "answer": "Tuition ranges from ₦500,000 to ₦800,000"}
            ]
    
    def find_answer(self, query):
        query = query.lower().strip()
        
        # 1. Exact match
        for qa in self.qa_data:
            if query == qa["question"]:
                return qa["answer"]
        
        # 2. Partial match
        for qa in self.qa_data:
            if qa["question"] in query or query in qa["question"]:
                return qa["answer"]
        
        # 3. Keyword fallback
        keyword_responses = {
            "admiss": "For admissions, visit crescent.edu.ng/admissions",
            "fee": "See fee details at crescent.edu.ng/fees",
            "course": "Browse programs at crescent.edu.ng/courses"
        }
        for kw, response in keyword_responses.items():
            if kw in query:
                return response
        
        return None

# --- Main Application ---
def main():
    # Initialize components
    personality = Personality()
    memory = ConversationMemory()
    nlp = NLPEngine()
    knowledge_base = KnowledgeBase()
    
    # Streamlit UI setup
    st.title("🎓 Crescent University Assistant")
    st.caption("Your human-like campus guide")
    
    # Initialize session state
    if "messages" not in st.session_state:
        st.session_state.messages = []
        st.session_state.messages.append({
            "role": "assistant",
            "content": personality.get_greeting()
        })
    
    # Display chat history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
    
    # Process user input
    if prompt := st.chat_input("Type your message..."):
        # Add user message to history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Generate response
        with st.chat_message("assistant"):
            # Step 1: Analyze query
            sentiment = nlp.analyze_sentiment(prompt)
            corrected_query = nlp.correct_typos(
                prompt.lower(),
                [qa["question"] for qa in knowledge_base.qa_data]
            )
            
            # Step 2: Build response components
            response_parts = []
            
            # Add thinking filler (50% chance)
            if random.random() < 0.5:
                response_parts.append(personality.get_filler())
            
            # Get factual answer
            answer = knowledge_base.find_answer(corrected_query) or \
                    "I'm still learning about that. Please email info@crescent.edu.ng"
            
            # Add emotional tone
            if sentiment == "positive":
                answer += random.choice([" 😊", "! Great question!"])
            elif sentiment == "negative":
                answer = "I understand your concern. " + answer
            
            response_parts.append(answer)
            
            # Add follow-up (30% chance)
            if random.random() < 0.3:
                if memory.context["user_interests"]:
                    topic = random.choice(list(memory.context["user_interests"]))
                    response_parts.append(
                        f"By the way, you mentioned {topic} earlier - need more details?"
                    )
            
            # Combine all parts
            full_response = " ".join(response_parts)
            
            # Display with typing effect
            display_text = ""
            placeholder = st.empty()
            for char in full_response:
                display_text += char
                placeholder.markdown(display_text + "▌")
                time.sleep(random.uniform(0.02, 0.07))
            placeholder.markdown(display_text)
        
        # Update conversation memory
        memory.update(prompt, full_response)
        st.session_state.messages.append({
            "role": "assistant",
            "content": full_response
        })

if __name__ == "__main__":
    main()
