import streamlit as st
from sentence_transformers import SentenceTransformer, util
import openai
import json
import os

# ====== Configuration ======
openai.api_key = os.getenv("OPENAI_API_KEY")

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

    response = openai.ChatCompletion.create(
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
    with st.spinner("Thinking..."):
        similar_qas = find_similar_questions(user_input)
        answer = generate_gpt_answer(user_input, similar_qas, st.session_state.chat_history)

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
