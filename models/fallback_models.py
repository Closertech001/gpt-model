import random
from typing import Dict, List
from sentence_transformers import SentenceTransformer
from transformers import pipeline
import torch

class FallbackGenerator:
    def __init__(self, config):
        self.config = config
        self.small_llm = None
        self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
        self.init_models()
        
        # Predefined responses for common questions
        self.fallback_responses = {
            "admission": "Admission requirements include 5 O'Level credits including Math and English. Cut-off marks vary by department.",
            "fees": "Undergraduate fees range from ₦500,000 to ₦800,000 per session depending on your department.",
            "accommodation": "Hostel fees are ₦150,000 per session. Off-campus options are available near the university.",
            "default": "I'm having trouble accessing detailed information. Please contact admissions@crescent.edu.ng for specific queries."
        }

    def init_models(self):
        """Initialize smaller local models"""
        try:
            # Tiny LLM for basic generation (only loads when needed)
            self.small_llm = pipeline(
                "text-generation",
                model="microsoft/Phi-3-mini-4k-instruct",
                torch_dtype=torch.float16,
                device_map="auto"
            )
        except Exception as e:
            print(f"Couldn't load local LLM: {e}")

    def generate(self, query: str) -> str:
        """Multi-stage fallback response generation"""
        # Stage 1: Check if question matches known categories
        category_response = self._match_category(query)
        if category_response:
            return category_response
        
        # Stage 2: Use local LLM if available
        if self.small_llm:
            return self._local_llm_response(query)
        
        # Stage 3: Semantic fallback to closest known question
        return self._semantic_fallback(query)

    def _match_category(self, query: str) -> str:
        """Match against predefined categories"""
        query_lower = query.lower()
        categories = {
            "admission": ["admission", "apply", "requirement", "jamb"],
            "fees": ["fee", "tuition", "payment", "school fee"],
            "accommodation": ["hostel", "housing", "residence", "accommodation"]
        }
        
        for category, keywords in categories.items():
            if any(kw in query_lower for kw in keywords):
                return self.fallback_responses[category]
        return None

    def _local_llm_response(self, query: str) -> str:
        """Generate response using local LLM"""
        prompt = f"""You are Crescent University's assistant. Provide a concise answer to this student query:
        
        Query: {query}
        Answer: """
        
        try:
            response = self.small_llm(
                prompt,
                max_new_tokens=150,
                do_sample=True,
                temperature=0.7
            )[0]['generated_text']
            return response.split("Answer: ")[-1].strip()
        except Exception:
            return self._semantic_fallback(query)

    def _semantic_fallback(self, query: str) -> str:
        """Find the closest matching question from knowledge base"""
        # Implement semantic search similar to main engine
        # (using the local embedder)
        return self.fallback_responses["default"]
