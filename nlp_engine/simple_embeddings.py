"""
Simple TF-IDF based embeddings - No external model downloads needed
Fast, lightweight alternative to sentence transformers
"""

from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
import pickle
import os
from typing import List


class SimpleTfidfEmbeddings:
    """
    Simple TF-IDF based embedding generator
    No model downloads required - works out of the box
    """
    
    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            max_features=768,  # Match dimension of sentence transformers
            ngram_range=(1, 2),
            min_df=1,
            lowercase=True
        )
        self.is_fitted = False
        self.embedding_dimension = 768
        print("✓ Simple TF-IDF embedding system initialized (no downloads needed)")
    
    def fit(self, texts: List[str]):
        """Fit the vectorizer on texts"""
        self.vectorizer.fit(texts)
        self.is_fitted = True
    
    def generate_embedding(self, text: str) -> np.ndarray:
        """Generate embedding for a single text"""
        if not self.is_fitted:
            # Auto-fit on first use
            self.fit([text])
        
        vector = self.vectorizer.transform([text]).toarray()[0]
        
        # Pad to 768 dimensions if needed
        if len(vector) < 768:
            vector = np.pad(vector, (0, 768 - len(vector)))
        else:
            vector = vector[:768]
        
        return vector
    
    def generate_embeddings_batch(self, texts: List[str], batch_size: int = 32) -> np.ndarray:
        """Generate embeddings for multiple texts"""
        if not self.is_fitted:
            self.fit(texts)
        
        vectors = self.vectorizer.transform(texts).toarray()
        
        # Pad all vectors to 768 dimensions
        padded_vectors = []
        for vector in vectors:
            if len(vector) < 768:
                vector = np.pad(vector, (0, 768 - len(vector)))
            else:
                vector = vector[:768]
            padded_vectors.append(vector)
        
        return np.array(padded_vectors)
    
    def compute_similarity(self, text1: str, text2: str) -> float:
        """Compute cosine similarity between two texts"""
        emb1 = self.generate_embedding(text1)
        emb2 = self.generate_embedding(text2)
        
        similarity = np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2) + 1e-10)
        return float(similarity)
    
    def save(self, filepath: str):
        """Save the vectorizer"""
        with open(filepath, 'wb') as f:
            pickle.dump(self.vectorizer, f)
    
    def load(self, filepath: str):
        """Load the vectorizer"""
        with open(filepath, 'rb') as f:
            self.vectorizer = pickle.load(f)
            self.is_fitted = True


# Alias for compatibility
LocalEmbeddingGenerator = SimpleTfidfEmbeddings
