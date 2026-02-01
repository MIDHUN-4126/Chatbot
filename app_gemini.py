"""
Flask Web Application with Gemini API Integration
Web interface for the Government Services Chatbot with AI-powered navigation
"""

from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS
import sys
import os
from datetime import datetime
import uuid
import requests
import keyring

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from chatbot_engine.chatbot import GovernmentChatbot

# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'your-secret-key-change-in-production'
CORS(app)

# Initialize chatbot (will be loaded on first request)
chatbot = None
gemini_model = None
KB_PATH = 'data/knowledge_base'
DB_PATH = 'data/scraped/government_data.db'

# Gemini API Configuration - Stored securely in Windows Credential Manager
SERVICE_NAME = 'TN_Gov_Chatbot'
API_KEY_NAME = 'GEMINI_API_KEY'

def get_api_key():
    """Retrieve API key from secure storage"""
    try:
        return keyring.get_password(SERVICE_NAME, API_KEY_NAME)
    except Exception as e:
        print(f"Error retrieving API key: {e}")
        return None


def initialize_gemini():
    """Initialize Gemini API"""
    global gemini_model
    api_key = get_api_key()
    if not api_key:
        print("⚠️ Warning: GEMINI_API_KEY not found in secure storage")
        print("   Run 'python setup_gemini_key.py' to set your API key")
        return None
    
    try:
        # Store API key for REST API calls
        gemini_model = {'api_key': api_key}
        print("✓ Gemini API initialized successfully (using REST API)")
        return gemini_model
    except Exception as e:
        print(f"❌ Error initializing Gemini: {e}")
        return None


def get_chatbot():
    """Get or initialize chatbot instance"""
    global chatbot
    if chatbot is None:
        try:
            chatbot = GovernmentChatbot(KB_PATH, DB_PATH)
        except Exception as e:
            print(f"Error initializing chatbot: {e}")
            return None
    return chatbot


def get_gemini_navigation_response(user_message, context=""):
    """Get Gemini-powered response for website navigation"""
    if not gemini_model:
        print("⚠ Gemini model not initialized")
        return None
    
    try:
        # Create a prompt specifically for TN e-Sevai website navigation
        prompt = f"""You are an expert assistant for the Tamil Nadu e-Sevai Portal (https://www.tnesevai.tn.gov.in/).

Website Context:
- TN e-Sevai is the official Tamil Nadu Government online services portal
- Provides government certificates and services online
- Services include: Birth Certificate, Income Certificate, Community Certificate, Ration Card, etc.
- Users need to login or register to apply for services

User's question: {user_message}

Knowledge base context: {context}

Your task as a website navigation assistant:
1. Guide users on how to navigate the TN e-Sevai website
2. Explain step-by-step where to click and what to do
3. Help with login, registration, and service application processes
4. Provide information about required documents
5. Be specific about menu items, buttons, and navigation paths
6. Speak in a friendly, helpful tone
7. If the user asks to navigate or perform an action, provide clear instructions

Provide a helpful, conversational response with specific navigation instructions:"""
        
        print(f"🤖 Calling Gemini API for: {user_message[:50]}...")
        
        # Use REST API directly - more reliable
        # Using gemini-flash-latest as generic fallback
        api_key = gemini_model['api_key']
        # url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent?key={api_key}"
        
        headers = {'Content-Type': 'application/json'}
        data = {
            "contents": [{
                "parts": [{"text": prompt}]
            }]
        }
        
        try:
            response = requests.post(url, headers=headers, json=data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                text = result['candidates'][0]['content']['parts'][0]['text']
                print(f"✓ Gemini responded successfully")
                return text
            else:
                raise Exception(f"API returned {response.status_code}: {response.text}")
        except Exception as e:
            print(f"❌ Error with Gemini API request: {e}")
            return None

    except Exception as e:
        print(f"❌ Error in get_gemini_navigation_response: {e}")
        import traceback
        traceback.print_exc()
        return None


@app.route('/')
def index():
    """Render main chat interface"""
    # Initialize session ID if not exists
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
    
    return render_template('index.html')


@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat messages with Gemini integration"""
    try:
        data = request.get_json()
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return jsonify({
                'success': False,
                'error': 'Empty message'
            }), 400
        
        # Initialize Gemini if not already done
        global gemini_model
        if gemini_model is None:
            initialize_gemini()
        
        # Initialize Gemini first - it's the primary handler now
        if gemini_model is None:
            initialize_gemini()
        
        # Try Gemini first (primary mode)
        if gemini_model:
            # Get knowledge base context (optional)
            context = ""
            try:
                bot = get_chatbot()
                if bot:
                    bot_response = bot.chat(user_message)
                    context = bot_response['text']
            except Exception as e:
                print(f"⚠ Could not get local context: {e}")
            
            # Let Gemini handle everything
            gemini_response = get_gemini_navigation_response(user_message, context)
            
            if gemini_response:
                print(f"✓ Gemini handled query: {user_message[:50]}...")
                return jsonify({
                    'success': True,
                    'response': gemini_response,
                    'type': 'gemini_full',
                    'language': 'en',
                    'enhanced': True,
                    'timestamp': datetime.now().isoformat()
                })
        
        # Fallback to local chatbot only if Gemini fails
        print(f"⚠ Gemini unavailable, using local chatbot for: {user_message[:50]}...")
        bot = get_chatbot()
        if bot is None:
            return jsonify({
                'success': False,
                'error': 'Both Gemini and local chatbot unavailable.'
            }), 500
        
        chatbot_response = bot.chat(user_message)
        
        return jsonify({
            'success': True,
            'response': chatbot_response['text'],
            'type': chatbot_response['type'],
            'language': chatbot_response['language'],
            'enhanced': False,
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        print(f"Error in chat endpoint: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    bot = get_chatbot()
    return jsonify({
        'status': 'ok' if bot else 'error',
        'chatbot_ready': bot is not None,
        'gemini_ready': gemini_model is not None,
        'mode': 'gemini_enhanced',
        'timestamp': datetime.now().isoformat()
    })


@app.route('/api/stats', methods=['GET'])
def stats():
    """Get chatbot statistics"""
    bot = get_chatbot()
    if not bot:
        return jsonify({'error': 'Chatbot not ready'}), 500
    
    return jsonify({
        'documents': bot.knowledge_base.vector_store.get_document_count(),
        'conversations': len(bot.conversation_history),
        'embedding_dimension': bot.embedding_generator.embedding_dimension,
        'gemini_enabled': gemini_model is not None
    })


if __name__ == '__main__':
    print("\n" + "="*60)
    print("Government Services Chatbot - Gemini Enhanced Mode")
    print("="*60 + "\n")
    
    # Initialize Gemini
    initialize_gemini()
    
    # Check if knowledge base exists
    if not os.path.exists(KB_PATH):
        print("❌ Error: Knowledge base not found!")
        print("\nPlease run these steps first:")
        print("  1. python data_collection/static_data.py")
        print("  2. python knowledge_base/build_index.py")
        print("\n" + "="*60 + "\n")
        sys.exit(1)
    
    print("✓ Knowledge base found")
    if gemini_model:
        print("✓ Gemini API ready - Enhanced navigation enabled")
    else:
        print("⚠️ Gemini API not available - Using fallback mode")
    print("✓ Starting web server...")
    print("\n" + "="*60)
    print("Server running at: http://localhost:5000")
    print("Mode: Gemini-Enhanced Website Navigation")
    print("Press Ctrl+C to stop")
    print("="*60 + "\n")
    
    # Run Flask app
    app.run(host='0.0.0.0', port=5000, debug=True)
