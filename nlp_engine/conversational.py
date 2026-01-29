"""
Conversational AI Engine - Simplified Version
Makes the chatbot more natural and human-like without heavy models
"""

import logging
import random

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ConversationalEngine:
    """
    Simplified conversational wrapper without heavy models
    """
    
    def __init__(self):
        logger.info("Using simplified conversational engine")
    
    def make_conversational(self, query: str, factual_response: str, language: str = 'en') -> str:
        """Make response more conversational with templates"""
        
        # Detect if it's a greeting
        if any(word in query.lower() for word in ['வணக்கம்', 'hello', 'hi', 'hey']):
            return factual_response
        
        # Bilingual conversational elements
        if language == 'tamil' or any(ord(c) >= 0x0B80 and ord(c) <= 0x0BFF for c in factual_response[:50]):
            openings = [
                "நிச்சயமாக! உங்களுக்கு உதவ மகிழ்ச்சி. ",
                "சரி! நான் விளக்குகிறேன். ",
                "நல்ல கேள்வி! ",
            ]
            closings = [
                "\n\nவேறு ஏதாவது தெரிந்து கொள்ள வேண்டுமா? 😊",
                "\n\nமேலும் விவரங்கள் தேவையா என்று தெரியப்படுத்துங்கள்!",
                "\n\nவேறு கேள்விகள் இருந்தால் கேளுங்கள்! 🙏",
            ]
        else:
            openings = [
                "Sure! Let me help you with that. ",
                "I'd be happy to help! ",
                "Great question! Here's what you need to know: ",
                "Let me explain that for you. ",
                "I can definitely help you with this. ",
            ]
            closings = [
                "\n\nIs there anything else you'd like to know? 😊",
                "\n\nFeel free to ask if you need more details!",
                "\n\nLet me know if you need any clarification! I'm here to help. 🙏",
                "\n\nHope this helps! Ask me anything else you need. 👍",
            ]
        
        opening = random.choice(openings)
        closing = random.choice(closings)
        
        return f"{opening}\n\n{factual_response}{closing}"

class SimplifiedConversationalEngine:
    """Same as ConversationalEngine - keeping for compatibility"""
    def __init__(self):
        self.engine = ConversationalEngine()
    
    def make_conversational(self, query: str, factual_response: str, language: str = 'en') -> str:
        return self.engine.make_conversational(query, factual_response, language)


# Choose which engine to use
def get_conversational_engine(use_huggingface: bool = False):
    """
    Get conversational engine - always returns simplified version
    
    Args:
        use_huggingface: Ignored, always uses simplified engine
    """
    return ConversationalEngine()
