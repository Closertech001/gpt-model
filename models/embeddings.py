import os
from sentence_transformers import SentenceTransformer
import torch
from typing import List, Union
from pathlib import Path
import pickle

class EmbeddingModel:
    def __init__(self, config):
        self.config = config
        self.model = self._load_model()
        self.cache_path = Path(config["data_path"]) / "embedding_cache.pkl"
        self.cache = self._load_cache()

    def _load_model(self) -> SentenceTransformer:
        """Load embedding model with error handling"""
        try:
            return SentenceTransformer(self.config["embedding_model"])
        except Exception as e:
            raise RuntimeError(f"Failed to load embedding model: {str(e)}")

    def _load_cache(self) -> dict:
        """Load embedding cache if exists"""
        if os.path.exists(self.cache_path):
            with open(self.cache_path, "rb") as f:
                return pickle.load(f)
        return {}

    def _save_cache(self):
        """Persist embedding cache"""
        with open(self.cache_path, "wb") as f:
            pickle.dump(self.cache, f)

    def encode(self, texts: Union[str, List[str]], normalize: bool = True) -> torch.Tensor:
        """
        Encode text(s) into embeddings with caching
        Args:
            texts: Single text or list of texts
            normalize: Whether to normalize embeddings to unit length
        Returns:
            Tensor of embeddings (shape: [num_texts, embedding_dim])
        """
        if isinstance(texts, str):
            texts = [texts]

        # Check cache first
        uncached_texts = []
        cached_embeddings = []
        for text in texts:
            if text in self.cache:
                cached_embeddings.append(self.cache[text])
            else:
                uncached_texts.append(text)

        # Encode uncached texts
        if uncached_texts:
            new_embeddings = self.model.encode(
                uncached_texts,
                convert_to_tensor=True,
                normalize_embeddings=normalize
            )
            
            # Update cache
            for text, emb in zip(uncached_texts, new_embeddings):
                self.cache[text] = emb.cpu()  # Store on CPU to save GPU memory
            self._save_cache()

            # Combine results
            if cached_embeddings:
                all_embeddings = torch.vstack([
                    torch.stack(cached_embeddings),
                    new_embeddings
                ])
            else:
                all_embeddings = new_embeddings
        else:
            all_embeddings = torch.stack(cached_embeddings)

        return all_embeddings

    def clear_cache(self):
        """Clear the embedding cache"""
        self.cache = {}
        if os.path.exists(self.cache_path):
            os.remove(self.cache_path)
