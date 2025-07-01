from pathlib import Path
import os

def load_config():
    return {
        "data_path": Path(os.getenv("DATA_PATH", "./data")),
        "abbreviations_path": Path("./data/abbreviations.csv"),
        "welcome_message": "Hello! I'm your Crescent University assistant. How can I help?",
        "banned_words": ["fuck", "shit", "idiot"],  # Expand this list
        "abuse_response": "I can't assist with that language. Please rephrase your question.",
        "embedding_model": "all-mpnet-base-v2"
    }
