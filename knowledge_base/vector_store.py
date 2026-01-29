"""
Simple Vector Store using NumPy
Local vector database for semantic search - Lightweight version
"""

import numpy as np
import pickle
import os
from typing import List, Dict, Tuple
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SimpleVectorStore:
    """
    Simple NumPy-based vector store for similarity search
    Lightweight alternative to FAISS
    """
    
    def __init__(self, dimension: int = 768, index_type: str = 'flat'):
        """
        Initialize simple vector store
        
        Args:
            dimension: Embedding dimension
            index_type: Kept for compatibility (always uses simple search)
        """
        self.dimension = dimension
        self.index_type = 'simple'
        self.documents: List[Dict] = []
        self.embeddings: np.ndarray = None
        
        logger.info(f"Simple vector store created: dimension: {dimension}")
    
    def add_documents(self, embeddings: np.ndarray, documents: List[Dict]):
        """
        Add documents with their embeddings to the index
        
        Args:
            embeddings: Numpy array of embeddings (n_docs x dimension)
            documents: List of document metadata dictionaries
        """
        if len(embeddings) != len(documents):
            raise ValueError("Number of embeddings must match number of documents")
        
        # Store embeddings
        if self.embeddings is None:
            self.embeddings = embeddings
        else:
            self.embeddings = np.vstack([self.embeddings, embeddings])
        
        self.documents.extend(documents)
        
        logger.info(f"Added {len(documents)} documents. Total: {len(self.documents)}")
    
    def search(self, query_embedding: np.ndarray, k: int = 5) -> List[Tuple[int, float, Dict]]:
        """
        Search for similar documents using cosine similarity
        
        Args:
            query_embedding: Query embedding vector
            k: Number of results to return
            
        Returns:
            List of tuples (index, distance, document)
        """
        if self.embeddings is None or len(self.embeddings) == 0:
            return []
        
        # Ensure query is 1D
        if query_embedding.ndim > 1:
            query_embedding = query_embedding.flatten()
        
        # Compute cosine similarities
        similarities = []
        for idx, doc_emb in enumerate(self.embeddings):
            # Cosine similarity
            sim = np.dot(query_embedding, doc_emb) / (
                np.linalg.norm(query_embedding) * np.linalg.norm(doc_emb) + 1e-10
            )
            similarities.append((idx, sim))
        
        # Sort by similarity (descending)
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        # Convert similarity to distance (lower is better)
        results = []
        for idx, sim in similarities[:k]:
            distance = 1.0 - sim  # Convert similarity to distance
            results.append((idx, distance, self.documents[idx]))
        
        return results
    
    def get_document_count(self) -> int:
        """Get total number of documents in index"""
        return len(self.documents)
    
    def save(self, directory: str):
        """
        Save index and documents to disk
        
        Args:
            directory: Directory to save files
        """
        os.makedirs(directory, exist_ok=True)
        
        # Save embeddings
        emb_path = os.path.join(directory, 'embeddings.npy')
        if self.embeddings is not None:
            np.save(emb_path, self.embeddings)
        
        # Save documents
        docs_path = os.path.join(directory, 'documents.pkl')
        with open(docs_path, 'wb') as f:
            pickle.dump(self.documents, f)
        
        # Save metadata
        meta_path = os.path.join(directory, 'metadata.pkl')
        metadata = {
            'dimension': self.dimension,
            'index_type': self.index_type,
            'document_count': len(self.documents)
        }
        with open(meta_path, 'wb') as f:
            pickle.dump(metadata, f)
        
        logger.info(f"Vector store saved to {directory}")
    
    def load(self, directory: str):
        """
        Load index and documents from disk
        
        Args:
            directory: Directory containing saved files
        """
        # Load metadata
        meta_path = os.path.join(directory, 'metadata.pkl')
        with open(meta_path, 'rb') as f:
            metadata = pickle.load(f)
        
        # Load embeddings
        emb_path = os.path.join(directory, 'embeddings.npy')
        if os.path.exists(emb_path):
            self.embeddings = np.load(emb_path)
        
        # Load documents
        docs_path = os.path.join(directory, 'documents.pkl')
        with open(docs_path, 'rb') as f:
            self.documents = pickle.load(f)
        
        self.dimension = metadata['dimension']
        self.index_type = metadata['index_type']
        
        logger.info(f"Vector store loaded from {directory}")
        logger.info(f"  Documents: {len(self.documents)}")


class KnowledgeBase:
    """
    Knowledge base combining vector store with document management
    """
    
    def __init__(self, embedding_dimension: int = 768):
        self.vector_store = SimpleVectorStore(dimension=embedding_dimension)
        self.embedding_dimension = embedding_dimension
        logger.info("Knowledge Base initialized")
    
    def add_from_database(self, db_path: str, embedding_generator):
        """
        Load data from SQLite database and add to knowledge base
        
        Args:
            db_path: Path to SQLite database
            embedding_generator: Embedding generator instance
        """
        import sqlite3
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Load services
        cursor.execute('SELECT * FROM services')
        rows = cursor.fetchall()
        
        documents = []
        texts = []
        
        for row in rows:
            # Create document with both English and Tamil
            doc = {
                'id': row[0],
                'name_en': row[1],
                'name_ta': row[2],
                'description_en': row[3],
                'description_ta': row[4],
                'department': row[5],
                'type': 'service'
            }
            
            # Combine text for embedding
            text = f"{row[1]} {row[2]} {row[3]} {row[4]}"
            
            documents.append(doc)
            texts.append(text)
        
        conn.close()
        
        # Generate embeddings
        logger.info(f"Generating embeddings for {len(texts)} documents...")
        embeddings = embedding_generator.generate_embeddings_batch(texts)
        
        # Add to vector store
        self.vector_store.add_documents(embeddings, documents)
        
        logger.info(f"✓ Added {len(documents)} documents to knowledge base")
    
    def search(self, query: str, embedding_generator, k: int = 5) -> List[Dict]:
        """
        Search knowledge base with natural language query
        
        Args:
            query: User query (Tamil or English)
            embedding_generator: Embedding generator instance
            k: Number of results
            
        Returns:
            List of relevant documents with scores
        """
        # Generate query embedding
        query_embedding = embedding_generator.generate_embedding(query)
        
        # Search vector store
        results = self.vector_store.search(query_embedding, k=k)
        
        # Format results
        formatted_results = []
        for idx, distance, doc in results:
            doc['similarity_score'] = 1.0 / (1.0 + distance)  # Convert distance to similarity
            formatted_results.append(doc)
        
        return formatted_results
    
    def save(self, directory: str):
        """Save knowledge base to disk"""
        self.vector_store.save(directory)
    
    def load(self, directory: str):
        """Load knowledge base from disk"""
        self.vector_store.load(directory)


def test_knowledge_base():
    """Test knowledge base functionality"""
    print("\n" + "="*60)
    print("Testing Knowledge Base")
    print("="*60 + "\n")
    
    # This would be run after data collection
    print("Note: This test requires:")
    print("  1. Run data_collection/static_data.py first")
    print("  2. Embeddings model downloaded")
    print("\nTest skipped. Run build_index.py to build full knowledge base.")


if __name__ == '__main__':
    test_knowledge_base()
