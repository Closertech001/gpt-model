from pathlib import Path
import os
from dotenv import load_dotenv
import json

load_dotenv()  # Load environment variables from .env file

class Config:
    def __init__(self):
        # Path configurations
        self.BASE_DIR = Path(__file__).parent.parent
        self.DATA_DIR = self.BASE_DIR / "data"
        self.LOGS_DIR = self.BASE_DIR / "logs"
        
        # Create directories if they don't exist
        self.DATA_DIR.mkdir(exist_ok=True)
        self.LOGS_DIR.mkdir(exist_ok=True)
        
        # File paths
        self.QA_DATASET = self.DATA_DIR / "qa_dataset.json"
        self.ABBREVIATIONS = self.DATA_DIR / "abbreviations.csv"
        self.SYNONYMS = self.DATA_DIR / "synonyms.csv"
        self.CONVERSATION_LOG = self.LOGS_DIR / "conversations.json"
        self.ANALYTICS_LOG = self.LOGS_DIR / "analytics.json"
        
        # Model configurations
        self.EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-mpnet-base-v2")
        self.FALLBACK_MODEL = os.getenv("FALLBACK_MODEL", "local/phi-3-mini")
        
        # Chat settings
        self.WELCOME_MESSAGE = """
        Welcome to Crescent University Assistant! 
        I can help with:
        - Admissions
        - Courses
        - Fees
        - Accommodation
        How may I assist you today?
        """
        
        # Safety settings
        self.BANNED_WORDS = self._load_banned_words()
        self.ABUSE_RESPONSE = """
        I'm sorry, but I can't respond to that language. 
        Please rephrase your question respectfully.
        """
    
    def _load_banned_words(self):
        default_words = ["fuck", "shit", "bitch", "idiot", "dumbass"]
        custom_words_path = self.DATA_DIR / "banned_words.txt"
        
        if custom_words_path.exists():
            with open(custom_words_path) as f:
                return [line.strip() for line in f if line.strip()]
        return default_words

# Singleton configuration instance
config = Config()
