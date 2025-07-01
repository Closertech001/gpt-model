from pathlib import Path
import os
import torch
from dotenv import load_dotenv
from typing import Dict, Any, Optional

class ConfigManager:
    """Centralized configuration management with environment awareness"""
    
    def __init__(self):
        load_dotenv()  # Load .env file if exists
        self._validate_paths()
        
    @property
    def settings(self) -> Dict[str, Any]:
        """Main configuration dictionary"""
        return {
            # --- Path Configurations ---
            "base_dir": Path(__file__).parent.parent,
            "data_dir": self._get_path("DATA_DIR", "data"),
            "log_dir": self._get_path("LOG_DIR", "logs"),
            
            # --- Model Configurations ---
            "embedding_model": os.getenv("EMBEDDING_MODEL", "all-mpnet-base-v2"),
            "fallback_model": os.getenv("FALLBACK_MODEL", "microsoft/Phi-3-mini-4k-instruct"),
            "local_llm_device": self._detect_device(),
            
            # --- API Configurations ---
            "use_openai": bool(int(os.getenv("USE_OPENAI", "1"))),
            "openai_model": os.getenv("OPENAI_MODEL", "gpt-4"),
            "openai_temp": float(os.getenv("OPENAI_TEMP", "0.5")),
            
            # --- Content Configurations ---
            "welcome_message": os.getenv(
                "WELCOME_MSG", 
                "Hello! I'm your Crescent University assistant. How can I help?"
            ),
            "abuse_response": os.getenv(
                "ABUSE_RESPONSE",
                "I can't assist with that language. Please rephrase your question."
            ),
            
            # --- File Paths ---
            "qa_dataset_path": self._get_data_path("QA_DATASET", "qa_dataset.json"),
            "abbreviations_path": self._get_data_path("ABBREVIATIONS", "abbreviations.csv"),
            "synonyms_path": self._get_data_path("SYNONYMS", "synonyms.csv"),
            "banned_words_path": self._get_data_path("BANNED_WORDS", "banned_words.txt"),
            
            # --- Performance ---
            "max_conversation_history": int(os.getenv("MAX_HISTORY", "10")),
            "embedding_cache": bool(int(os.getenv("EMBEDDING_CACHE", "1"))),
        }
    
    def _get_path(self, env_var: str, default: str) -> Path:
        """Resolve directory paths with environment variable override"""
        path_str = os.getenv(env_var, default)
        path = Path(path_str)
        if not path.is_absolute():
            path = Path(__file__).parent.parent / path
        return path
    
    def _get_data_path(self, env_var: str, default: str) -> Path:
        """Resolve data file paths with validation"""
        path = self._get_path(env_var, default)
        if not path.exists():
            raise FileNotFoundError(f"Required data file not found: {path}")
        return path
    
    def _validate_paths(self) -> None:
        """Ensure required directories exist"""
        paths_to_create = [
            self._get_path("DATA_DIR", "data"),
            self._get_path("LOG_DIR", "logs")
        ]
        for path in paths_to_create:
            path.mkdir(exist_ok=True)
    
    def _detect_device(self) -> str:
        """Auto-detect best device for local models"""
        if torch.cuda.is_available():
            return "cuda"
        elif torch.backends.mps.is_available():
            return "mps"
        return "cpu"
    
    def get_banned_words(self) -> list:
        """Load banned words dynamically"""
        with open(self.settings["banned_words_path"]) as f:
            return [line.strip() for line in f if line.strip()]

# Singleton instance for easy access
config = ConfigManager().settings

# Example usage:
if __name__ == "__main__":
    print("Current configuration:")
    for key, value in config.items():
        print(f"{key}: {value}")
