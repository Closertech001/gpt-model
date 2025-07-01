from pathlib import Path
import os
import json
import torch
from dotenv import load_dotenv
from typing import Dict, Any, List
import streamlit as st

class ConfigManager:
    """Robust configuration manager with JSON validation"""
    
    def __init__(self):
        load_dotenv()
        self.base_dir = Path(__file__).parent.parent
        self._validate_paths()
        
    @property
    def settings(self) -> Dict[str, Any]:
        return {
            "data_dir": self.base_dir / "data",
            "abbreviations": self._load_abbreviations(),
            "synonyms": self._load_synonyms(),
            "qa_data": self._load_qa_data(),
            "device": self._detect_device()
        }
    
    def _detect_device(self) -> str:
        return "cuda" if torch.cuda.is_available() else "cpu"
    
    def _validate_paths(self) -> None:
        (self.base_dir / "data").mkdir(exist_ok=True)
    
    def _load_abbreviations(self) -> Dict[str, str]:
        default = {"u": "you", "r": "are"}
        path = self.base_dir / "data" / "abbreviations.csv"
        try:
            if path.exists():
                with open(path) as f:
                    return dict(line.strip().split(",", 1) for line in f if line.strip())
            return default
        except Exception as e:
            st.warning(f"Abbreviations load failed: {e}")
            return default
    
    def _load_synonyms(self) -> Dict[str, str]:
        default = {"hod": "head of department"}
        path = self.base_dir / "data" / "synonyms.csv"
        try:
            if path.exists():
                with open(path) as f:
                    return dict(line.strip().split(",", 1) for line in f if line.strip())
            return default
        except Exception as e:
            st.warning(f"Synonyms load failed: {e}")
            return default
    
    def _load_qa_data(self) -> List[Dict[str, str]]:
        path = self.base_dir / "data" / "qa_dataset.json"
        if not path.exists():
            st.error(f"QA dataset missing at {path}")
            return []
        
        try:
            with open(path) as f:
                data = json.load(f)
                if not isinstance(data, list):
                    raise ValueError("QA data must be a list of dicts")
                return data
        except json.JSONDecodeError as e:
            st.error(f"Invalid JSON in QA file: {e}")
            return []
        except Exception as e:
            st.error(f"QA data load failed: {e}")
            return []

config = ConfigManager().settings
