from typing import Optional
from transformers import pipeline, AutoModelForCausalLM, AutoTokenizer
import torch
from pathlib import Path
import warnings
import logging

class FallbackGenerator:
    def __init__(self, config):
        self.config = config
        self.model = None
        self.tokenizer = None
        self._init_fallback_model()

    def _init_fallback_model(self):
        """Initialize local LLM with graceful fallback"""
        try:
            # Try to load a small efficient model first
            model_name = "microsoft/phi-2"  # 2.7B param model
            
            self.tokenizer = AutoTokenizer.from_pretrained(
                model_name,
                trust_remote_code=True
            )
            
            self.model = AutoModelForCausalLM.from_pretrained(
                model_name,
                torch_dtype="auto",
                device_map="auto",
                trust_remote_code=True
            )
            
            logging.info("Local fallback model loaded successfully")
            
        except Exception as e:
            warnings.warn(f"Failed to load local LLM: {str(e)}")
            self.model = None

    def generate(self, prompt: str, max_length: int = 200) -> str:
        """
        Generate response using local model when primary fails
        Args:
            prompt: User query with conversation history
            max_length: Maximum response length
        Returns:
            Generated response text
        """
        if self.model is None:
            return self._ultra_fallback(prompt)

        try:
            inputs = self.tokenizer(
                f"Question: {prompt}\nAnswer:",
                return_tensors="pt",
                return_attention_mask=False
            ).to(self.model.device)

            outputs = self.model.generate(
                **inputs,
                max_length=max_length,
                temperature=0.7,
                do_sample=True
            )
            
            response = self.tokenizer.decode(
                outputs[0],
                skip_special_tokens=True
            )
            
            # Extract only the answer part
            return response.split("Answer:")[-1].strip()

        except Exception as e:
            logging.error(f"Fallback generation failed: {str(e)}")
            return self._ultra_fallback(prompt)

    def _ultra_fallback(self, prompt: str) -> str:
        """Final fallback when even local LLM fails"""
        # Simple rule-based responses
        if any(kw in prompt.lower() for kw in ["admission", "apply"]):
            return "For admission queries, please visit: https://crescent.edu.ng/admissions"
        elif "fee" in prompt.lower():
            return "Fee structures vary by program. Contact bursary@crescent.edu.ng"
        else:
            return "I couldn't process your request. Please email info@crescent.edu.ng for assistance."

    def save_model_locally(self, save_path: Path):
        """Save model for offline use"""
        if self.model:
            self.model.save_pretrained(save_path)
            self.tokenizer.save_pretrained(save_path)
