from pathlib import Path
import os
import torch
from dotenv import load_dotenv
from typing import Dict, Any
import streamlit as st

class ConfigManager:
    """Safe configuration manager for Streamlit Cloud"""
    
    def __init__(self):
        load_dotenv()
        self.base_dir = Path(__file__).parent.parent
        self._validate_paths()
        
    @property
    def settings(self) -> Dict[str, Any]:
        return {
            # Path configurations
            "data_dir": self.base_dir / "data",
            "log_dir": self.base_dir / "logs",
            
            # Model configurations
            "embedding_model": "all-MiniLM-L6-v2",
            "fallback_model": "microsoft/Phi-3-mini-4k-instruct",
            "device": self._detect_device(),
            
            # API configurations
            "use_openai": True,
            "openai_model": "gpt-3.5-turbo",
            
            # File paths (with existence checks)
            "abbreviations": self._load_abbreviations(),
            "synonyms": self._load_synonyms(),
            "qa_data": self._load_qa_data()
        }
    
    def _detect_device(self) -> str:
        """Auto-select best available device"""
        if torch.cuda.is_available():
            return "cuda"
        return "cpu"
    
    def _validate_paths(self) -> None:
        """Ensure required directories exist"""
        (self.base_dir / "data").mkdir(exist_ok=True)
        (self.base_dir / "logs").mkdir(exist_ok=True)
    
    def _load_abbreviations(self) -> Dict[str, str]:
        """Load abbreviations with fallback"""
        default = {"u": "you", "r": "are"}  # Embedded fallback
        try:
            with open(self.base_dir / "data" / "abbreviations.csv") as f:
                return {line.split(",")[0]: line.split(",")[1].strip() 
                        for line in f if line.strip()}
        except FileNotFoundError:
            st.warning("Using default abbreviations")
            return default
    
    def _load_synonyms(self) -> Dict[str, str]:
        """Load synonyms with fallback"""
        default = {"hod": "head of department"}
        try:
            with open(self.base_dir / "data" / "synonyms.csv") as f:
                return {line.split(",")[0]: line.split(",")[1].strip() 
                        for line in f if line.strip()}
        except FileNotFoundError:
            st.warning("Using default synonyms")
            return default
    
    def _load_qa_data(self) -> Dict[str, str]:
        """Load QA dataset with empty fallback"""
        try:
            with open(self.base_dir / "data" / "qa_dataset.json") as f:
                return json.load(f)
        except FileNotFoundError:
            st.error("QA dataset missing! Some features may not work")
            return []

# Singleton instance
config = ConfigManager().settings
