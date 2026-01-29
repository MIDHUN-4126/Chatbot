"""
Build Knowledge Base Index
Creates vector index from scraped/static government data
"""

import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from knowledge_base.vector_store import KnowledgeBase
from nlp_engine.simple_embeddings import LocalEmbeddingGenerator
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def build_knowledge_base():
    """Build knowledge base from collected data"""
    
    print("\n" + "="*60)
    print("Building Knowledge Base")
    print("="*60 + "\n")
    
    # Check if data exists
    data_path = '../data/scraped/government_data.db'
    if not os.path.exists(data_path):
        print("❌ Error: Government data not found!")
        print("\nPlease run one of these first:")
        print("  python data_collection/static_data.py")
        print("  python data_collection/scraper.py")
        return
    
    # Initialize components
    print("Step 1: Loading embedding model...")
    embedding_generator = LocalEmbeddingGenerator()
    
    print("\nStep 2: Initializing knowledge base...")
    kb = KnowledgeBase(embedding_dimension=embedding_generator.embedding_dimension)
    
    print("\nStep 3: Loading data from database...")
    kb.add_from_database(data_path, embedding_generator)
    
    print("\nStep 4: Saving knowledge base...")
    kb_path = '../data/knowledge_base'
    kb.save(kb_path)
    
    print("\n" + "="*60)
    print("✓ Knowledge Base Built Successfully!")
    print("="*60)
    print(f"  Location: {kb_path}")
    print(f"  Documents: {kb.vector_store.get_document_count()}")
    print(f"  Embedding dimension: {kb.embedding_dimension}")
    print("\nNext step: Run 'python app.py' to start the chatbot")
    print("="*60 + "\n")


def test_search():
    """Test searching the knowledge base"""
    
    print("\n" + "="*60)
    print("Testing Knowledge Base Search")
    print("="*60 + "\n")
    
    kb_path = '../data/knowledge_base'
    if not os.path.exists(kb_path):
        print("❌ Knowledge base not found. Run build_knowledge_base() first.")
        return
    
    # Load
    print("Loading knowledge base...")
    embedding_generator = LocalEmbeddingGenerator()
    kb = KnowledgeBase(embedding_dimension=embedding_generator.embedding_dimension)
    kb.load(kb_path)
    
    # Test queries
    test_queries = [
        "பிறப்பு சான்றிதழ் எப்படி பெறுவது?",
        "How to apply for income certificate?",
        "ரேஷன் அட்டை கட்டணம் என்ன?",
    ]
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        results = kb.search(query, embedding_generator, k=3)
        
        print("\nTop results:")
        for i, result in enumerate(results, 1):
            print(f"  {i}. {result.get('name_en', 'N/A')} / {result.get('name_ta', 'N/A')}")
            print(f"     Score: {result['similarity_score']:.3f}")
    
    print("\n" + "="*60)


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'test':
        test_search()
    else:
        build_knowledge_base()
