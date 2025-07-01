import json
from typing import Dict, Tuple
from sentence_transformers import util
from models.embeddings import EmbeddingModel
from models.fallback_models import FallbackGenerator
from core.preprocessing import TextNormalizer
from core.memory_manager import MemoryManager

class ChatEngine:
    def __init__(self, config):
        self.config = config
        self.embedder = EmbeddingModel(config)
        self.normalizer = TextNormalizer(config)
        self.memory = MemoryManager(config)
        self.fallback = FallbackGenerator(config)
        
        # Load knowledge base
        with open(config["data_path"]/"qa_dataset.json") as f:
            self.qa_data = json.load(f)
        
        # Precompute embeddings
        self.question_embeds = self.embedder.encode(
            [q["question"] for q in self.qa_data]
        )

    def process_query(self, user_input: str) -> str:
        """End-to-end query processing pipeline"""
        # Step 1: Preprocess
        clean_input = self.normalizer.normalize(user_input)
        
        # Step 2: Safety check
        if self.normalizer.is_abusive(clean_input):
            return config["abuse_response"]
        
        # Step 3: Update context
        self.memory.update_context(clean_input)
        
        # Step 4: Generate response
        response, confidence = self._generate_response(clean_input)
        
        # Step 5: Post-process
        if confidence < 0.4:
            return self.memory.request_clarification()
        return self._enrich_response(response)

    def _generate_response(self, query: str) -> Tuple[str, float]:
        """Multi-stage response generation"""
        # Stage 1: Exact match
        for qa in self.qa_data:
            if query.lower() == qa["question"].lower():
                return qa["answer"], 1.0
        
        # Stage 2: Semantic search
        query_embed = self.embedder.encode(query)
        scores = util.pytorch_cos_sim(query_embed, self.question_embeds)[0]
        top_idx = scores.argmax().item()
        
        if scores[top_idx] > 0.6:
            return self.qa_data[top_idx]["answer"], float(scores[top_idx])
        
        # Stage 3: LLM generation
        try:
            llm_response = self._call_llm(query)
            return llm_response, 0.5
        except Exception:
            return self.fallback.generate(query), 0.3
            
    # Add to ChatEngine class
    def _call_llm(self, query: str) -> str:
        """Attempt LLM response with fallback"""
        try:
            if self.config["use_openai"]:  # Set in config
                messages = self.memory.build_llm_prompt(query)
                response = openai.ChatCompletion.create(
                    model="gpt-4",
                    messages=messages,
                    temperature=0.5
                )
                return response.choices[0].message.content
            raise Exception("OpenAI disabled in config")  # Force fallback
        except Exception as e:
            print(f"LLM Error: {e}")
            return self.fallback.generate(query)
