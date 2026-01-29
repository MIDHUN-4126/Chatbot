"""
Local Embedding Generator
Uses sentence-transformers with multilingual models for generating embeddings
No external API calls - completely local processing
"""

from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List, Union
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LocalEmbeddingGenerator:
    """
    Generate text embeddings using local multilingual models
    Supports Tamil, English, and other Indian languages
    """
    
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        """
        Initialize embedding generator with multilingual model
        
        Args:
            model_name: Sentence transformer model name
                - 'paraphrase-multilingual-mpnet-base-v2' (default): Best for multilingual
                - 'distiluse-base-multilingual-cased-v2': Faster, lighter
        """
        logger.info(f"Loading embedding model: {model_name}")
        
        try:
            self.model = SentenceTransformer(model_name)
            self.model_name = model_name
            self.embedding_dimension = self.model.get_sentence_embedding_dimension()
            
            logger.info(f"✓ Model loaded successfully")
            logger.info(f"  Embedding dimension: {self.embedding_dimension}")
            
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            raise
    
    def generate_embedding(self, text: str) -> np.ndarray:
        """
        Generate embedding for a single text
        
        Args:
            text: Input text (Tamil or English)
            
        Returns:
            Numpy array of embeddings
        """
        try:
            embedding = self.model.encode(text, convert_to_numpy=True)
            return embedding
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            return np.zeros(self.embedding_dimension)
    
    def generate_embeddings_batch(self, texts: List[str], batch_size: int = 32) -> np.ndarray:
        """
        Generate embeddings for multiple texts (batch processing)
        
        Args:
            texts: List of input texts
            batch_size: Batch size for processing
            
        Returns:
            Numpy array of embeddings (n_texts x embedding_dim)
        """
        try:
            embeddings = self.model.encode(
                texts, 
                batch_size=batch_size,
                show_progress_bar=True,
                convert_to_numpy=True
            )
            return embeddings
        except Exception as e:
            logger.error(f"Error generating batch embeddings: {e}")
            return np.zeros((len(texts), self.embedding_dimension))
    
    def compute_similarity(self, text1: str, text2: str) -> float:
        """
        Compute cosine similarity between two texts
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Similarity score (0 to 1)
        """
        emb1 = self.generate_embedding(text1)
        emb2 = self.generate_embedding(text2)
        
        # Cosine similarity
        similarity = np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))
        
        return float(similarity)
    
    def find_most_similar(self, query: str, candidates: List[str], top_k: int = 5) -> List[tuple]:
        """
        Find most similar texts from candidates
        
        Args:
            query: Query text
            candidates: List of candidate texts
            top_k: Number of top results to return
            
        Returns:
            List of tuples (index, similarity_score)
        """
        query_emb = self.generate_embedding(query)
        candidate_embs = self.generate_embeddings_batch(candidates)
        
        # Compute similarities
        similarities = []
        for idx, cand_emb in enumerate(candidate_embs):
            similarity = np.dot(query_emb, cand_emb) / (
                np.linalg.norm(query_emb) * np.linalg.norm(cand_emb)
            )
            similarities.append((idx, float(similarity)))
        
        # Sort by similarity
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        return similarities[:top_k]
    
    def save_embeddings(self, embeddings: np.ndarray, filepath: str):
        """Save embeddings to file"""
        np.save(filepath, embeddings)
        logger.info(f"Embeddings saved to {filepath}")
    
    def load_embeddings(self, filepath: str) -> np.ndarray:
        """Load embeddings from file"""
        embeddings = np.load(filepath)
        logger.info(f"Embeddings loaded from {filepath}")
        return embeddings


def test_embedding_generator():
    """Test the embedding generator"""
    print("\n" + "="*60)
    print("Testing Local Embedding Generator")
    print("="*60 + "\n")
    
    # Initialize
    generator = LocalEmbeddingGenerator()
    
    # Test texts
    test_texts = [
        "பிறப்பு சான்றிதழ் எப்படி பெறுவது?",
        "How to get birth certificate?",
        "வருமான சான்றிதழ் விண்ணப்பிக்க என்ன ஆவணங்கள் தேவை?",
        "What documents are needed for income certificate?",
        "ரேஷன் அட்டை நிலையை எப்படி பார்ப்பது?"
    ]
    
    print("Generating embeddings...")
    embeddings = generator.generate_embeddings_batch(test_texts)
    
    print(f"\n✓ Generated {len(embeddings)} embeddings")
    print(f"  Embedding dimension: {embeddings.shape[1]}")
    
    # Test similarity
    print("\nTesting similarity:")
    query = "How to apply for birth certificate?"
    print(f"\nQuery: {query}")
    print("\nMost similar texts:")
    
    results = generator.find_most_similar(query, test_texts, top_k=3)
    for idx, score in results:
        print(f"  {score:.3f} - {test_texts[idx]}")
    
    print("\n" + "="*60)


if __name__ == '__main__':
    test_embedding_generator()
