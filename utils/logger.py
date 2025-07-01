import json
from datetime import datetime
from pathlib import Path
from .config import config
import uuid

class ChatLogger:
    def __init__(self):
        self.session_id = str(uuid.uuid4())
        self.analytics = {
            "session_start": datetime.now().isoformat(),
            "queries": 0,
            "average_response_time": 0,
            "fallbacks_used": 0,
            "unanswered_questions": []
        }

    def log_conversation(self, user_input: str, response: str):
        """Log complete conversation"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "session_id": self.session_id,
            "user_input": user_input,
            "response": response,
            "response_time": self._get_last_response_time()
        }
        
        # Append to conversation log
        with open(config.CONVERSATION_LOG, "a") as f:
            f.write(json.dumps(entry) + "\n")
        
        # Update analytics
        self._update_analytics(user_input, response)

    def _update_analytics(self, user_input: str, response: str):
        self.analytics["queries"] += 1
        
        if "I don't know" in response:
            self.analytics["unanswered_questions"].append(user_input)
        
        if "fallback" in response.lower():
            self.analytics["fallbacks_used"] += 1
        
        # Save analytics snapshot
        with open(config.ANALYTICS_LOG, "w") as f:
            json.dump(self.analytics, f)

    def _get_last_response_time(self) -> float:
        # Implement actual timing logic
        return 0.0

    def get_analytics(self):
        return self.analytics
