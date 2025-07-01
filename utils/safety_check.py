from transformers import pipeline
from .config import config
from typing import Tuple
import re

class SafetyChecker:
    def __init__(self):
        # Initialize hate speech classifier
        self.toxicity_classifier = pipeline(
            "text-classification",
            model="unitary/toxic-bert",
            device="cpu"
        )
        
        # Compile regex patterns
        self.banned_pattern = re.compile(
            r'\b(' + '|'.join(map(re.escape, config.BANNED_WORDS)) + r')\b', 
            flags=re.IGNORECASE
        )
        self.pii_pattern = re.compile(
            r'\b\d{10}\b|\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        )

    def check_input(self, text: str) -> Tuple[bool, str]:
        """Comprehensive safety check"""
        # Check for banned words
        if self.banned_pattern.search(text):
            return False, "banned_words"
        
        # Check for PII
        if self.pii_pattern.search(text):
            return False, "pii_detected"
        
        # Check toxicity
        result = self.toxicity_classifier(text[:512])[0]
        if result["label"] == "toxic" and result["score"] > 0.85:
            return False, "toxic_content"
        
        return True, ""

    def get_safety_response(self, violation_type: str) -> str:
        """Appropriate responses for different violations"""
        responses = {
            "banned_words": config.ABUSE_RESPONSE,
            "pii_detected": """
            For your privacy, please don't share personal information.
            Ask your question without including emails, phone numbers, etc.
            """,
            "toxic_content": """
            I aim to maintain respectful conversations. 
            Could you please rephrase your question more politely?
            """
        }
        return responses.get(violation_type, config.ABUSE_RESPONSE)
