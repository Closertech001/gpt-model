class TextNormalizer:
    def __init__(self, config):
        self.abbreviations = self._load_dynamic_dict(config["abbreviations_path"])
        self.synonyms = self._load_dynamic_dict(config["synonyms_path"])
    
    def normalize(self, text: str) -> str:
        """Pipeline for text cleaning"""
        text = text.lower().strip()
        text = self._correct_spelling(text)
        text = self._expand_abbreviations(text)
        text = self._standardize_synonyms(text)
        return text
    
    def is_abusive(self, text: str) -> bool:
        """Enhanced toxicity check"""
        return any(bad_word in text for bad_word in self.config["banned_words"])
