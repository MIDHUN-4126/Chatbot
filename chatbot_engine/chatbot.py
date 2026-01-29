"""
Chatbot Engine
Core chatbot logic with intent recognition and response generation
No external LLM APIs - completely local processing
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from nlp_engine.text_processor import BilingualNLPEngine
from nlp_engine.simple_embeddings import LocalEmbeddingGenerator
# Conversational engine import - optional for more natural responses
try:
    from nlp_engine.conversational import get_conversational_engine
    CONVERSATIONAL_AVAILABLE = True
except ImportError:
    CONVERSATIONAL_AVAILABLE = False
from knowledge_base.vector_store import KnowledgeBase
import sqlite3
import json
from typing import Dict, List
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GovernmentChatbot:
    """
    Main chatbot engine for government service navigation
    Handles query understanding, information retrieval, and response generation
    """
    
    def __init__(self, knowledge_base_path: str, db_path: str):
        """
        Initialize chatbot with knowledge base
        
        Args:
            knowledge_base_path: Path to vector store
            db_path: Path to SQLite database
        """
        logger.info("Initializing Government Chatbot...")
        
        # Load NLP components
        self.nlp_engine = BilingualNLPEngine()
        self.embedding_generator = LocalEmbeddingGenerator()
        
        # Load conversational engine (makes responses more natural)
        if CONVERSATIONAL_AVAILABLE:
            self.conversational_engine = get_conversational_engine(use_huggingface=False)
        else:
            self.conversational_engine = None
        
        # Load knowledge base
        self.knowledge_base = KnowledgeBase(
            embedding_dimension=self.embedding_generator.embedding_dimension
        )
        
        if os.path.exists(knowledge_base_path):
            self.knowledge_base.load(knowledge_base_path)
            logger.info(f"✓ Knowledge base loaded: {self.knowledge_base.vector_store.get_document_count()} documents")
        else:
            logger.warning(f"Knowledge base not found at {knowledge_base_path}")
        
        # Database connection
        self.db_path = db_path
        
        # Conversation context
        self.conversation_history = []
        self.last_service = None  # Track last discussed service
        self.user_context = {}  # Store user preferences and context
        
        # Response templates
        self.response_templates = self._load_response_templates()
        
        logger.info("✓ Chatbot initialized successfully")
    
    def _load_response_templates(self) -> Dict:
        """Load bilingual response templates"""
        return {
            'greeting': {
                'en': "Hello! I'm here to help you with Tamil Nadu government services. How can I assist you today?",
                'ta': "வணக்கம்! தமிழ்நாடு அரசு சேவைகள் தொடர்பாக நான் உங்களுக்கு உதவ இங்கே இருக்கிறேன். இன்று நான் உங்களுக்கு எப்படி உதவ முடியும்?"
            },
            'farewell': {
                'en': "Thank you for using our service. Have a great day!",
                'ta': "எங்கள் சேவையைப் பயன்படுத்தியதற்கு நன்றி. நல்ல நாள்!"
            },
            'clarification': {
                'en': "I'm not sure I understand. Could you please rephrase your question?",
                'ta': "எனக்கு புரியவில்லை. உங்கள் கேள்வியை வேறு விதமாக கேட்க முடியுமா?"
            },
            'no_results': {
                'en': "I couldn't find specific information about that. Please try asking differently or contact the helpline: 1800-425-1000",
                'ta': "அதைப் பற்றி குறிப்பிட்ட தகவல் எனக்கு கிடைக்கவில்லை. தயவுசெய்து வேறுவிதமாக கேளுங்கள் அல்லது உதவி எண்ணை தொடர்பு கொள்ளுங்கள்: 1800-425-1000"
            }
        }
    
    def get_service_details(self, service_id: str) -> Dict:
        """Get detailed service information from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM services WHERE id = ?', (service_id,))
        row = cursor.fetchone()
        
        conn.close()
        
        if row:
            return {
                'id': row[0],
                'name_en': row[1],
                'name_ta': row[2],
                'description_en': row[3],
                'description_ta': row[4],
                'department': row[5],
                'department_ta': row[6],
                'requirements': json.loads(row[7]) if row[7] else [],
                'requirements_ta': json.loads(row[8]) if row[8] else [],
                'procedure': json.loads(row[9]) if row[9] else [],
                'procedure_ta': json.loads(row[10]) if row[10] else [],
                'fees': row[11],
                'fees_ta': row[12],
                'processing_time': row[13],
                'contact': row[14],
                'url': row[15]
            }
        
        return None
    
    def generate_response(self, query_analysis: Dict, search_results: List[Dict]) -> Dict:
        """
        Generate appropriate response based on query analysis and search results
        
        Args:
            query_analysis: Analyzed query from NLP engine
            search_results: Retrieved documents from knowledge base
            
        Returns:
            Response dictionary with text and metadata
        """
        language = query_analysis['language']
        intent = query_analysis['intent']
        service_type = query_analysis['service_type']
        original_text = query_analysis['original_text'].lower()
        
        # Handle greetings
        if self.nlp_engine.is_greeting(query_analysis['original_text']):
            return {
                'text': self.response_templates['greeting']['ta' if language == 'tamil' else 'en'],
                'type': 'greeting',
                'language': language
            }
        
        # Handle farewells
        if self.nlp_engine.is_farewell(query_analysis['original_text']):
            return {
                'text': self.response_templates['farewell']['ta' if language == 'tamil' else 'en'],
                'type': 'farewell',
                'language': language
            }
        
        # Handle follow-up questions (yes/no/more/tell me more)
        if self._is_follow_up(original_text):
            return self._handle_follow_up(language, intent)
        
        # Handle vague or unclear queries - ask clarifying questions
        if self._is_vague_query(original_text):
            return self._ask_clarification(language, original_text)
        
        # No results found
        if not search_results or search_results[0]['similarity_score'] < 0.5:
            return self._handle_no_results(language, service_type)
        
        # Get most relevant result
        top_result = search_results[0]
        service_id = top_result.get('id')
        
        # Get detailed information
        service_details = self.get_service_details(service_id)
        
        if not service_details:
            return {
                'text': self.response_templates['no_results']['ta' if language == 'tamil' else 'en'],
                'type': 'no_results',
                'language': language
            }
        
        # Store for follow-up questions
        self.last_service = service_details
        
        # Generate intent-specific response
        return self._format_service_response(service_details, intent, language)
    
    def _format_service_response(self, service: Dict, intent: str, language: str) -> Dict:
        """Format service information based on intent"""
        
        is_tamil = (language == 'tamil')
        
        # Service name
        service_name = service['name_ta'] if is_tamil else service['name_en']
        description = service['description_ta'] if is_tamil else service['description_en']
        
        response_parts = []
        
        # Always include service name
        response_parts.append(f"📋 {service_name}")
        response_parts.append("")
        
        # Intent-specific information (tailored to user's actual request)
        if intent == 'download':
            if is_tamil:
                response_parts.append("💻 ஆன்லைனில் டவுன்லோட் செய்வது எப்படி:")
                response_parts.append("  1. {0} வலைதளத்திற்கு செல்லவும்".format(service['url']))
                response_parts.append("  2. உங்கள் விண்ணப்ப எண் மற்றும் விவரங்களை உள்ளிடவும்")
                response_parts.append("  3. 'பதிவிறக்கம்' பொத்தானை கிளிக் செய்யவும்")
                response_parts.append("  4. PDF ஐப் பதிவிறக்கம் செய்து அச்சிடவும்")
                response_parts.append("")
                response_parts.append("⚠️ குறிப்பு: ஏற்கனவே வழங்கப்பட்ட சான்றிதழ்களை மட்டுமே டவுன்லோட் செய்ய முடியும்")
            else:
                response_parts.append("💻 How to Download Online:")
                response_parts.append("  1. Visit {0}".format(service['url']))
                response_parts.append("  2. Enter your application number and details")
                response_parts.append("  3. Click 'Download' button")
                response_parts.append("  4. Download PDF and print")
                response_parts.append("")
                response_parts.append("⚠️ Note: Only previously issued certificates can be downloaded")
        
        elif intent == 'reissue':
            if is_tamil:
                response_parts.append("🔄 நகல் சான்றிதழ் பெறுவது எப்படி:")
                response_parts.append("  1. அருகிலுள்ள இ-சேவை மையம் அல்லது தாலுக்கா அலுவலகத்திற்கு செல்லவும்")
                response_parts.append("  2. 'நகல் சான்றிதழ்' விண்ணப்பத்தைப் பூர்த்தி செய்யவும்")
                response_parts.append("  3. அசல் சான்றிதழின் நகல் அல்லது எண்ணை வழங்கவும்")
                response_parts.append("  4. அடையாள சான்று சமர்ப்பிக்கவும்")
                response_parts.append("  5. கட்டணம் செலுத்தவும்")
                response_parts.append("")
                response_parts.append(f"💰 கட்டணம்: {service.get('fees_ta', 'தகவல் இல்லை')}")
            else:
                response_parts.append("🔄 How to Get Duplicate Certificate:")
                response_parts.append("  1. Visit nearest e-Sevai center or Taluk office")
                response_parts.append("  2. Fill 'Duplicate Certificate' application")
                response_parts.append("  3. Provide original certificate copy or number")
                response_parts.append("  4. Submit ID proof")
                response_parts.append("  5. Pay fees")
                response_parts.append("")
                response_parts.append(f"💰 Fees: {service.get('fees', 'Not specified')}")
        
        elif intent == 'correction':
            if is_tamil:
                response_parts.append("✏️ தவறுகளைத் திருத்துவது எப்படி:")
                response_parts.append("  1. அசல் சான்றிதழுடன் தாலுக்கா அலுவலகத்திற்கு செல்லவும்")
                response_parts.append("  2. 'திருத்தம்' விண்ணப்பத்தை பூர்த்தி செய்யவும்")
                response_parts.append("  3. திருத்தத்திற்கான ஆதார ஆவணங்களை இணைக்கவும்")
                response_parts.append("  4. சரிபார்ப்புக்குப் பிறகு திருத்தப்பட்ட சான்றிதழ் வழங்கப்படும்")
            else:
                response_parts.append("✏️ How to Make Corrections:")
                response_parts.append("  1. Visit Taluk office with original certificate")
                response_parts.append("  2. Fill 'Correction' application form")
                response_parts.append("  3. Attach supporting documents for correction")
                response_parts.append("  4. Corrected certificate issued after verification")
        
        elif intent == 'renewal':
            if is_tamil:
                response_parts.append("🔄 புதுப்பிப்பது எப்படி:")
                response_parts.append("  1. இ-சேவை மையம் அல்லது ஆன்லைனில் விண்ணப்பிக்கவும்")
                response_parts.append("  2. அசல் சான்றிதழின் நகலை இணைக்கவும்")
                response_parts.append("  3. புதுப்பிக்கப்பட்ட தகவல்கள்/ஆவணங்களை சமர்ப்பிக்கவும்")
                response_parts.append("  4. கட்டணம் செலுத்தவும்")
            else:
                response_parts.append("🔄 How to Renew:")
                response_parts.append("  1. Apply at e-Sevai center or online")
                response_parts.append("  2. Attach copy of original certificate")
                response_parts.append("  3. Submit updated information/documents")
                response_parts.append("  4. Pay renewal fees")
        
        elif intent == 'status':
            if is_tamil:
                response_parts.append("📊 நிலையைச் சரிபார்ப்பது எப்படி:")
                response_parts.append("  1. {0} இல் 'விண்ணப்ப நிலை' பிரிவுக்கு செல்லவும்".format(service['url']))
                response_parts.append("  2. உங்கள் விண்ணப்ப எண்ணை உள்ளிடவும்")
                response_parts.append("  3. மொபைல் எண் அல்லது ஆதார் எண்ணைச் சரிபார்க்கவும்")
                response_parts.append("  4. தற்போதைய நிலையைக் காணவும்")
                response_parts.append("")
                response_parts.append(f"📞 SMS வழி நிலை: {service['contact']} க்கு அழைக்கவும்")
            else:
                response_parts.append("📊 How to Check Status:")
                response_parts.append("  1. Go to 'Application Status' section on {0}".format(service['url']))
                response_parts.append("  2. Enter your application number")
                response_parts.append("  3. Verify with mobile or Aadhaar number")
                response_parts.append("  4. View current status")
                response_parts.append("")
                response_parts.append(f"📞 Status via SMS: Call {service['contact']}")
        
        elif intent == 'documents':
            if is_tamil:
                response_parts.append("📑 தேவையான ஆவணங்கள்:")
                for req in service['requirements_ta']:
                    response_parts.append(f"  • {req}")
            else:
                response_parts.append("📑 Required Documents:")
                for req in service['requirements']:
                    response_parts.append(f"  • {req}")
        
        elif intent == 'apply' or intent == 'procedure':
            if is_tamil:
                response_parts.append("📝 விண்ணப்பிக்கும் முறை:")
                for i, step in enumerate(service['procedure_ta'], 1):
                    response_parts.append(f"  {i}. {step}")
            else:
                response_parts.append("📝 Application Procedure:")
                for i, step in enumerate(service['procedure'], 1):
                    response_parts.append(f"  {i}. {step}")
        
        elif intent == 'fees':
            fees = service['fees_ta'] if is_tamil else service['fees']
            fees_label = "கட்டணம்" if is_tamil else "Fees"
            response_parts.append(f"💰 {fees_label}: {fees}")
            if service.get('processing_time'):
                time_label = "செயலாக்க நேரம்" if is_tamil else "Processing Time"
                response_parts.append(f"⏱️ {time_label}: {service['processing_time']}")
        
        elif intent == 'contact':
            if is_tamil:
                response_parts.append("📞 தொடர்பு தகவல்:")
                response_parts.append(f"  உதவி எண்: {service['contact']}")
                response_parts.append(f"  வலைதளம்: {service['url']}")
                response_parts.append(f"  துறை: {service.get('department_ta', '')}")
            else:
                response_parts.append("📞 Contact Information:")
                response_parts.append(f"  Helpline: {service['contact']}")
                response_parts.append(f"  Website: {service['url']}")
                response_parts.append(f"  Department: {service.get('department', '')}")
        
        else:  # general_inquiry or eligibility
            response_parts.append(description)
            response_parts.append("")
            if is_tamil:
                response_parts.append("📑 தேவையான ஆவணங்கள்:")
                for req in service['requirements_ta']:
                    response_parts.append(f"  • {req}")
                response_parts.append("")
                response_parts.append("📝 விண்ணப்பிக்கும் முறை:")
                for i, step in enumerate(service['procedure_ta'], 1):
                    response_parts.append(f"  {i}. {step}")
            else:
                response_parts.append("📑 Required Documents:")
                for req in service['requirements']:
                    response_parts.append(f"  • {req}")
                response_parts.append("")
                response_parts.append("📝 Application Procedure:")
                for i, step in enumerate(service['procedure'], 1):
                    response_parts.append(f"  {i}. {step}")
            response_parts.append("")
            fees = service['fees_ta'] if is_tamil else service['fees']
            fees_label = "கட்டணம்" if is_tamil else "Fees"
            response_parts.append(f"💰 {fees_label}: {fees}")
            if service.get('processing_time'):
                time_label = "செயலாக்க நேரம்" if is_tamil else "Processing Time"
                response_parts.append(f"⏱️ {time_label}: {service['processing_time']}")
        
        # Contact information (always at end)
        response_parts.append("")
        if is_tamil:
            response_parts.append(f"📞 தொடர்பு: {service['contact']}")
            response_parts.append(f"🌐 வலைதளம்: {service['url']}")
        else:
            response_parts.append(f"📞 Contact: {service['contact']}")
            response_parts.append(f"🌐 Website: {service['url']}")
        
        factual_response = '\n'.join(response_parts)
        
        # Make it more conversational if available
        if self.conversational_engine:
            conversational_response = self.conversational_engine.make_conversational(
                "", factual_response, language
            )
        else:
            # Simple wrapper without conversational engine
            import random
            if language == 'tamil' or any(ord(c) >= 0x0B80 and ord(c) <= 0x0BFF for c in response_parts[0]):
                openings = ["நிச்சயமாக! ", "சரி! ", "நல்ல கேள்வி! "]
                closings = ["\n\nவேறு ஏதாவது தெரிந்து கொள்ள வேண்டுமா? 😊", "\n\nமேலும் விவரங்கள் தேவையா?"]
            else:
                openings = ["Sure! ", "I'd be happy to help! ", "Here's what you need to know: "]
                closings = ["\n\nIs there anything else you'd like to know? 😊", "\n\nFeel free to ask if you need more details!"]
            conversational_response = random.choice(openings) + factual_response + random.choice(closings)
        
        return {
            'text': conversational_response,
            'type': 'service_info',
            'language': language,
            'service_id': service['id'],
            'service_name': service_name
        }
    
    def _is_follow_up(self, text: str) -> bool:
        """Check if message is a follow-up question"""
        follow_up_words = [
            'yes', 'yeah', 'ok', 'okay', 'sure', 'more', 'tell me more', 'what else',
            'ஆம்', 'சரி', 'சொல்லுங்கள்', 'மேலும்', 'வேறு', 'அப்புறம்',
            'and then', 'next', 'after that', 'பிறகு', 'அடுத்து'
        ]
        return any(word in text.lower() for word in follow_up_words) and len(text.split()) < 5
    
    def _is_vague_query(self, text: str) -> bool:
        """Check if query is too vague"""
        vague_patterns = [
            'help', 'info', 'tell me', 'want to know', 'need',
            'உதவி', 'தகவல்', 'தெரிந்து', 'தேவை'
        ]
        # Vague if it's short and contains vague words but no specific service
        is_short = len(text.split()) < 4
        has_vague_word = any(word in text.lower() for word in vague_patterns)
        has_no_service = not any(service in text.lower() for service in [
            'birth', 'income', 'community', 'ration', 'certificate',
            'பிறப்பு', 'வருமான', 'சமூக', 'ரேஷன்', 'சான்றிதழ்'
        ])
        return is_short and has_vague_word and has_no_service
    
    def _ask_clarification(self, language: str, original_text: str) -> Dict:
        """Ask clarifying questions for vague queries"""
        if language == 'tamil':
            response = """நான் உங்களுக்கு உதவ விரும்புகிறேன்! 😊

நீங்கள் எந்த சேவையைப் பற்றி தெரிந்து கொள்ள விரும்புகிறீர்கள்?

🔹 பிறப்பு சான்றிதழ் (Birth Certificate)
🔹 வருமான சான்றிதழ் (Income Certificate)
🔹 சமூக சான்றிதழ் (Community Certificate)
🔹 ரேஷன் அட்டை (Ration Card)

இவற்றில் ஏதேனும் ஒன்றைத் தேர்ந்தெடுக்கவும் அல்லது உங்கள் கேள்வியை விரிவாகக் கூறவும்!"""
        else:
            response = """I'd love to help you! 😊

Which service would you like to know about?

🔹 Birth Certificate (பிறப்பு சான்றிதழ்)
🔹 Income Certificate (வருமான சான்றிதழ்)
🔹 Community Certificate (சமூக சான்றிதழ்)
🔹 Ration Card (ரேஷன் அட்டை)

You can click one of the quick replies below or tell me more about what you need!"""
        
        return {
            'text': response,
            'type': 'clarification',
            'language': language
        }
    
    def _handle_follow_up(self, language: str, intent: str) -> Dict:
        """Handle follow-up questions about last service"""
        if not self.last_service:
            if language == 'tamil':
                return {
                    'text': "நீங்கள் எந்த சேவையைப் பற்றி கேட்கிறீர்கள்? தயவுசெய்து குறிப்பிடவும்! 😊",
                    'type': 'clarification',
                    'language': language
                }
            else:
                return {
                    'text': "Which service are you asking about? Please let me know! 😊",
                    'type': 'clarification',
                    'language': language
                }
        
        # Provide additional details about the last service
        service = self.last_service
        is_tamil = language == 'tamil'
        
        if intent == 'procedure' or 'how' in intent:
            # Give detailed step-by-step procedure
            response_parts = []
            if is_tamil:
                response_parts.append(f"நிச்சயமாக! {service['name_ta']} க்கான விரிவான செயல்முறை:")
                response_parts.append("\n📝 படிப்படியான வழிமுறைகள்:")
                for i, step in enumerate(service['procedure_ta'], 1):
                    response_parts.append(f"\n{i}. {step}")
            else:
                response_parts.append(f"Sure! Here's the detailed procedure for {service['name_en']}:")
                response_parts.append("\n📝 Step-by-step process:")
                for i, step in enumerate(service['procedure'], 1):
                    response_parts.append(f"\n{i}. {step}")
        else:
            # Give complete information
            return self._format_service_response(service, 'general_inquiry', language)
        
        response_text = ''.join(response_parts)
        if is_tamil:
            response_text += "\n\nவேறு ஏதாவது தெரிந்து கொள்ள வேண்டுமா? 😊"
        else:
            response_text += "\n\nWould you like to know anything else? 😊"
        
        return {
            'text': response_text,
            'type': 'follow_up',
            'language': language
        }
    
    def _handle_no_results(self, language: str, service_type: str) -> Dict:
        """Provide helpful response when no results found"""
        if language == 'tamil':
            response = f"""மன்னிக்கவும், எனக்கு துல்லியமான தகவல் கிடைக்கவில்லை. 😔

ஆனால் நான் உங்களுக்கு உதவ முடியும்:

🔹 பிறப்பு சான்றிதழ் எப்படி பெறுவது?
🔹 வருமான சான்றிதழ் தேவையா?
🔹 ரேஷன் அட்டை விண்ணப்பம்?
🔹 சமூக சான்றிதழ் ஆவணங்கள்?

அல்லது எனக்கு உங்கள் கேள்வியை வேறு விதமாக கேளுங்கள்! 💚

தொடர்பு எண்: 1800-425-1000"""
        else:
            response = f"""I'm sorry, I couldn't find exact information about that. 😔

But I can help you with:

🔹 How to get Birth Certificate?
🔹 Need Income Certificate?
🔹 Ration Card application?
🔹 Community Certificate documents?

Or try asking your question differently! 💚

Helpline: 1800-425-1000"""
        
        return {
            'text': response,
            'type': 'no_results',
            'language': language
        }
    
    def chat(self, user_message: str) -> Dict:
        """
        Process user message and generate response
        
        Args:
            user_message: User's input message
            
        Returns:
            Response dictionary with text and metadata
        """
        logger.info(f"User: {user_message}")
        
        # Analyze query
        query_analysis = self.nlp_engine.analyze_query(user_message)
        logger.info(f"Analysis: {query_analysis['intent']} | {query_analysis['service_type']} | {query_analysis['language']}")
        
        # Search knowledge base
        search_results = self.knowledge_base.search(
            user_message,
            self.embedding_generator,
            k=3
        )
        
        # Generate response
        response = self.generate_response(query_analysis, search_results)
        
        # Save to conversation history
        self.conversation_history.append({
            'user': user_message,
            'bot': response['text'],
            'analysis': query_analysis
        })
        
        logger.info(f"Bot: {response['type']}")
        
        return response


def test_chatbot():
    """Test chatbot with sample queries"""
    
    print("\n" + "="*60)
    print("Government Chatbot - Interactive Test")
    print("="*60 + "\n")
    
    # Paths
    kb_path = '../data/knowledge_base'
    db_path = '../data/scraped/government_data.db'
    
    # Check if files exist
    if not os.path.exists(kb_path):
        print("❌ Error: Knowledge base not found!")
        print("\nPlease run these steps first:")
        print("  1. python data_collection/static_data.py")
        print("  2. python knowledge_base/build_index.py")
        return
    
    # Initialize chatbot
    print("Initializing chatbot...")
    chatbot = GovernmentChatbot(kb_path, db_path)
    
    print("\n" + "="*60)
    print("Chatbot ready! Type 'quit' to exit.")
    print("="*60 + "\n")
    
    # Test queries
    test_queries = [
        "வணக்கம்",
        "பிறப்பு சான்றிதழ் எப்படி பெறுவது?",
        "What documents are needed for income certificate?",
        "ரேஷன் அட்டை கட்டணம் என்ன?",
    ]
    
    print("Running test queries:\n")
    for query in test_queries:
        print(f"User: {query}")
        response = chatbot.chat(query)
        print(f"\nBot:\n{response['text']}\n")
        print("-" * 60 + "\n")
    
    # Interactive mode
    print("\n" + "="*60)
    print("Interactive Mode (type 'quit' to exit)")
    print("="*60 + "\n")
    
    while True:
        try:
            user_input = input("You: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'bye']:
                print("\nBot: Thank you! Goodbye!")
                break
            
            if not user_input:
                continue
            
            response = chatbot.chat(user_input)
            print(f"\nBot:\n{response['text']}\n")
        
        except KeyboardInterrupt:
            print("\n\nExiting...")
            break
        except Exception as e:
            print(f"Error: {e}")


if __name__ == '__main__':
    test_chatbot()
