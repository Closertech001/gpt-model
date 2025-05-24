
import streamlit as st
from sentence_transformers import SentenceTransformer, util
from openai import OpenAI
import json
import os
import random

# ====== Abbreviations dictionary and follow-up phrases ======
abbreviations = {
    "u": "you", "r": "are", "ur": "your", "ow": "how", "pls": "please", "plz": "please",
    "tmrw": "tomorrow", "cn": "can", "wat": "what", "cud": "could", "shud": "should",
    "wud": "would", "abt": "about", "bcz": "because", "bcoz": "because", "btw": "between",
    "asap": "as soon as possible", "idk": "i don't know", "imo": "in my opinion",
    "msg": "message", "doc": "document", "d": "the", "yr": "year", "sem": "semester",
    "dept": "department", "admsn": "admission", "cresnt": "crescent", "uni": "university",
    "clg": "college", "sch": "school", "info": "information"
}

FOLLOW_UP_PHRASES = [
    "what about", "how about", "and then", "next",
    "after that", "can you tell me more", "more info",
    "continue", "explain further", "go on", "what happened after"
]

# Initialize sym_spell for spelling correction
sym_spell = SymSpell(max_dictionary_edit_distance=2, prefix_length=7)

def normalize_text(text):
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s]', '', text)
    # Remove repeating characters more than twice (e.g. sooo -> so)
    text = re.sub(r'(.)\1{2,}', r'\1', text)
    return text

def preprocess_text(text):
    text = normalize_text(text)
    words = text.split()
    expanded = [abbreviations.get(word, word) for word in words]
    corrected = []
    for word in expanded:
        suggestions = sym_spell.lookup(word, Verbosity.CLOSEST, max_edit_distance=2)
        corrected.append(suggestions[0].term if suggestions else word)
    return ' '.join(corrected)

def is_follow_up(user_input):
    user_input = user_input.lower()
    return any(phrase in user_input for phrase in FOLLOW_UP_PHRASES)

@st.cache_resource
def load_model():
    return SentenceTransformer('all-MiniLM-L6-v2')

# ====== Greetings and responses ======
greetings = [
    "hi", "hello", "hey", "hi there", "greetings", "how are you",
    "how are you doing", "how's it going", "can we talk?",
    "can we have a conversation?", "okay", "i'm fine", "i am fine"
]

greeting_responses = [
    "Hello!", "Hi there!", "Hey!", "Greetings!",
    "I'm doing well, thank you!", "Sure pal", "Okay"
]

# ====== Initialize OpenAI Client ======
client = OpenAI(api_key=os.getenv("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"))

# ====== Load SentenceTransformer Model ======
@st.cache_resource
def load_model():
    return SentenceTransformer("all-MiniLM-L6-v2")

model = load_model()

# ====== Load Q&A Dataset ======
@st.cache_resource
def load_data():
    with open("qa_dataset.json", "r") as f:
        qa_pairs = json.load(f)
    questions = [item["question"] for item in qa_pairs]
    answers = [item["answer"] for item in qa_pairs]
    embeddings = model.encode(questions, convert_to_tensor=True)
    return qa_pairs, questions, answers, embeddings

qa_pairs, questions, answers, question_embeddings = load_data()

# ====== Helper functions ======

def expand_abbreviations(text):
    words = text.lower().split()
    expanded_words = [abbreviations.get(word, word) for word in words]
    return " ".join(expanded_words)

def is_follow_up(text):
    text_lower = text.lower()
    return any(phrase in text_lower for phrase in FOLLOW_UP_PHRASES)

def check_greeting(user_input):
    processed_input = user_input.lower().strip()
    if processed_input in greetings:
        return random.choice(greeting_responses)
    return None

# ====== Semantic Search ======
def find_similar_questions(user_input, top_k=3):
    query_embedding = model.encode(user_input, convert_to_tensor=True)
    hits = util.semantic_search(query_embedding, question_embeddings, top_k=top_k)[0]
    return [(questions[hit['corpus_id']], answers[hit['corpus_id']]) for hit in hits]

# ====== GPT Answer Generation ======
def generate_gpt_answer(user_question, top_matches, chat_history):
    context = "\n".join([f"Q: {q}\nA: {a}" for q, a in top_matches])
    messages = [{"role": "system", "content": "You are a helpful assistant for Crescent University."}]

    for turn in chat_history:
        messages.append({"role": "user", "content": turn["user"]})
        messages.append({"role": "assistant", "content": turn["bot"]})

    prompt = f"{context}\nUser's question: {user_question}\nAnswer:"
    messages.append({"role": "user", "content": prompt})

    response = client.chat.completions.create(
        model="gpt-4",
        messages=messages,
        temperature=0.5,
        max_tokens=300
    )
    return response.choices[0].message.content.strip()

# ====== Streamlit UI ======
st.set_page_config(page_title="Crescent University Chatbot", page_icon="🎓")
st.title("🎓 Crescent University Chatbot")
st.markdown("Ask any question about the university — even vague or incomplete!")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

user_input = st.text_input("Ask a question...")

if user_input:
    # First check greetings
    greeting_reply = check_greeting(user_input)
    if greeting_reply:
        st.markdown(f"**Bot:** {greeting_reply}")
        st.session_state.chat_history.append({
            "user": user_input,
            "bot": greeting_reply
        })
    else:
        # Expand abbreviations
        expanded_input = expand_abbreviations(user_input)

        # Check follow-up phrases (optional usage here, just info)
        if is_follow_up(expanded_input):
            st.info("Detected follow-up question, continuing the conversation...")

        with st.spinner("Thinking..."):
            similar_qas = find_similar_questions(expanded_input)
            answer = generate_gpt_answer(expanded_input, similar_qas, st.session_state.chat_history)

            st.markdown(f"**You:** {user_input}")
            st.markdown(f"**Bot:** {answer}")

            st.session_state.chat_history.append({
                "user": user_input,
                "bot": answer
            })

if st.session_state.chat_history:
    st.markdown("### 🗨️ Chat History")
    for turn in st.session_state.chat_history:
        st.markdown(f"**You:** {turn['user']}")
        st.markdown(f"**Bot:** {turn['bot']}")

if st.button("🔁 Reset Chat"):
    st.session_state.chat_history = []
    st.experimental_rerun()
