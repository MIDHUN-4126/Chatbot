"""
NLP Engine for Tamil and English Language Processing
Handles language detection, text preprocessing, and Tamil language support
"""

import re
from typing import List, Dict, Tuple
import unicodedata
from langdetect import detect
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TamilNLPProcessor:
    """
    Tamil language NLP processor
    Handles Tamil text preprocessing, tokenization, and normalization
    """
    
    # Tamil Unicode ranges
    TAMIL_UNICODE_RANGE = (0x0B80, 0x0BFF)
    
    # Common Tamil stopwords
    TAMIL_STOPWORDS = {
        'அது', 'இது', 'அந்த', 'இந்த', 'அவர்', 'இவர்', 'என்ன', 'எங்கு', 
        'எப்படி', 'எப்போது', 'எதற்கு', 'யார்', 'எது', 'எவ்வாறு',
        'ஒரு', 'மற்றும்', 'அல்லது', 'ஆனால்', 'உடன்', 'பின்',
        'முன்', 'மேல்', 'கீழ்', 'உள்ளே', 'வெளியே'
    }
    
    def __init__(self):
        logger.info("Initializing Tamil NLP Processor")
    
    def is_tamil_text(self, text: str) -> bool:
        """Check if text contains Tamil characters"""
        tamil_chars = 0
        total_chars = 0
        
        for char in text:
            if char.strip():
                total_chars += 1
                code_point = ord(char)
                if self.TAMIL_UNICODE_RANGE[0] <= code_point <= self.TAMIL_UNICODE_RANGE[1]:
                    tamil_chars += 1
        
        if total_chars == 0:
            return False
        
        return (tamil_chars / total_chars) > 0.3  # 30% threshold
    
    def normalize_tamil_text(self, text: str) -> str:
        """Normalize Tamil text"""
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        # Normalize unicode characters
        text = unicodedata.normalize('NFC', text)
        
        return text
    
    def tokenize_tamil(self, text: str) -> List[str]:
        """Tokenize Tamil text"""
        # Simple space-based tokenization for Tamil
        text = self.normalize_tamil_text(text)
        
        # Split by whitespace and punctuation
        tokens = re.findall(r'[\u0B80-\u0BFF]+|[a-zA-Z]+|\d+', text)
        
        return tokens
    
    def remove_stopwords(self, tokens: List[str]) -> List[str]:
        """Remove Tamil stopwords"""
        return [token for token in tokens if token not in self.TAMIL_STOPWORDS]
    
    def extract_keywords(self, text: str, top_n: int = 5) -> List[str]:
        """Extract keywords from Tamil text"""
        tokens = self.tokenize_tamil(text)
        filtered_tokens = self.remove_stopwords(tokens)
        
        # Count frequencies
        freq = {}
        for token in filtered_tokens:
            freq[token] = freq.get(token, 0) + 1
        
        # Sort by frequency
        sorted_tokens = sorted(freq.items(), key=lambda x: x[1], reverse=True)
        
        return [token for token, _ in sorted_tokens[:top_n]]


class BilingualNLPEngine:
    """
    Bilingual NLP Engine for Tamil and English
    Handles language detection and processing for both languages
    """
    
    def __init__(self):
        self.tamil_processor = TamilNLPProcessor()
        logger.info("Bilingual NLP Engine initialized")
        
        # Common government service keywords
        self.service_keywords = {
            'birth': ['birth', 'certificate', 'பிறப்பு', 'சான்றிதழ்'],
            'income': ['income', 'certificate', 'வருமான', 'சான்றிதழ்'],
            'community': ['community', 'caste', 'சமூக', 'ஜாதி'],
            'ration': ['ration', 'card', 'ரேஷன்', 'அட்டை'],
            'license': ['driving', 'license', 'ஓட்டுநர்', 'உரிமம்'],
            'passport': ['passport', 'பாஸ்போர்ட்'],
            'pension': ['pension', 'ஓய்வூதியம்'],
            'scholarship': ['scholarship', 'உதவித்தொகை']
        }
        
        # Intent keywords (order matters - check specific intents first)
        self.intent_keywords = {
            'download': ['download', 'get online', 'print', 'டவுன்லோட்', 'பதிவிறக்க', 'பிரிண்ட்', 'அச்சிட'],
            'reissue': ['reissue', 'duplicate', 'lost', 'மீண்டும்', 'நகல்', 'தொலைந்த'],
            'correction': ['correct', 'change', 'modify', 'update', 'edit', 'திருத்த', 'மாற்ற', 'திருத்தம்'],
            'renewal': ['renew', 'renewal', 'extend', 'புதுப்பிக்க', 'நீட்டிக்க'],
            'status': ['status', 'track', 'check status', 'progress', 'நிலை', 'கண்காணிக்க', 'எங்கே'],
            'apply': ['apply', 'application', 'new', 'first time', 'விண்ணப்பிக்க', 'விண்ணப்பம்', 'புதிய'],
            'documents': ['document', 'required', 'need what', 'ஆவணம்', 'தேவை', 'என்ன வேண்டும்'],
            'procedure': ['how to', 'process', 'procedure', 'steps', 'எப்படி', 'செயல்முறை', 'படிகள்'],
            'contact': ['contact', 'phone', 'email', 'helpline', 'தொடர்பு', 'எண்', 'உதவி'],
            'fees': ['fee', 'cost', 'charge', 'price', 'கட்டணம்', 'விலை', 'எவ்வளவு'],
            'eligibility': ['eligible', 'eligibility', 'qualify', 'தகுதி', 'யோக்கியதை']
        }
    
    def detect_language(self, text: str) -> str:
        """Detect language of input text"""
        try:
            if self.tamil_processor.is_tamil_text(text):
                return 'tamil'
            
            # Try langdetect for other languages
            lang = detect(text)
            if lang in ['en', 'hi']:
                return lang
            
            return 'unknown'
        except:
            return 'unknown'
    
    def preprocess_text(self, text: str) -> str:
        """Preprocess text for both Tamil and English"""
        # Convert to lowercase (for English)
        text_lower = text.lower()
        
        # Normalize Tamil text
        if self.detect_language(text) == 'tamil':
            text_lower = self.tamil_processor.normalize_tamil_text(text)
        
        # Remove extra whitespace
        text_lower = ' '.join(text_lower.split())
        
        return text_lower
    
    def extract_service_type(self, text: str) -> str:
        """Extract service type from user query"""
        text_lower = text.lower()
        
        for service, keywords in self.service_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    return service
        
        return 'general'
    
    def extract_intent(self, text: str) -> str:
        """Extract user intent from query"""
        text_lower = text.lower()
        
        # Check intents in priority order (specific to general)
        # Order is important - check download before apply, etc.
        for intent, keywords in self.intent_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    return intent  # Return first match (most specific)
        
        return 'general_inquiry'
    
    def analyze_query(self, user_query: str) -> Dict:
        """
        Analyze user query and extract:
        - Language
        - Intent
        - Service type
        - Keywords
        """
        language = self.detect_language(user_query)
        preprocessed_text = self.preprocess_text(user_query)
        intent = self.extract_intent(preprocessed_text)
        service_type = self.extract_service_type(preprocessed_text)
        
        # Extract keywords
        if language == 'tamil':
            keywords = self.tamil_processor.extract_keywords(user_query)
        else:
            # Simple keyword extraction for English
            keywords = [word for word in preprocessed_text.split() 
                       if len(word) > 3 and word.isalnum()][:5]
        
        return {
            'language': language,
            'intent': intent,
            'service_type': service_type,
            'keywords': keywords,
            'preprocessed_text': preprocessed_text,
            'original_text': user_query
        }
    
    def is_greeting(self, text: str) -> bool:
        """Check if text is a greeting"""
        greetings = [
            'வணக்கம்', 'hello', 'hi', 'hey', 'good morning', 'good afternoon',
            'good evening', 'வாழ்த்துக்கள்', 'நல்ல காலை', 'நல்ல பிற்பகல்'
        ]
        
        text_lower = text.lower()
        return any(greeting in text_lower for greeting in greetings)
    
    def is_farewell(self, text: str) -> bool:
        """Check if text is a farewell"""
        farewells = [
            'bye', 'goodbye', 'see you', 'thanks', 'thank you',
            'நன்றி', 'போய்வருகிறேன்', 'பிறகு பார்ப்போம்'
        ]
        
        text_lower = text.lower()
        return any(farewell in text_lower for farewell in farewells)


def test_nlp_engine():
    """Test the NLP engine with sample queries"""
    engine = BilingualNLPEngine()
    
    test_queries = [
        "வணக்கம், பிறப்பு சான்றிதழ் எப்படி பெறுவது?",
        "How to apply for income certificate?",
        "வருமான சான்றிதழுக்கு என்ன ஆவணங்கள் தேவை?",
        "What is the status of my ration card application?",
        "சமூக சான்றிதழ் கட்டணம் எவ்வளவு?",
    ]
    
    print("\n" + "="*60)
    print("NLP Engine Test Results")
    print("="*60 + "\n")
    
    for query in test_queries:
        result = engine.analyze_query(query)
        print(f"Query: {query}")
        print(f"  Language: {result['language']}")
        print(f"  Intent: {result['intent']}")
        print(f"  Service: {result['service_type']}")
        print(f"  Keywords: {', '.join(result['keywords'])}")
        print()


if __name__ == '__main__':
    test_nlp_engine()
