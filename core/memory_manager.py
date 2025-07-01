from collections import deque

class MemoryManager:
    def __init__(self, config):
        self.context = {
            "department": None,
            "level": None,
            "conversation": deque(maxlen=10)
        }
    
    def update_context(self, query: str):
        """Extract and store contextual clues"""
        if "computer science" in query:
            self.context["department"] = "Computer Science"
        # Add more context extraction rules
        
    def build_llm_prompt(self, query: str) -> list:
        """Convert memory into LLM prompt"""
        return [
            {"role": "system", "content": f"You're a Crescent Uni assistant. Current context: {self.context}"},
            *[{"role": "user", "content": msg["user"]} 
              for msg in self.context["conversation"]]
        ]
