"""
Flask Web Application
Web interface for the Government Services Chatbot
"""

from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS
import sys
import os
from datetime import datetime
import uuid

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from chatbot_engine.chatbot import GovernmentChatbot

# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'your-secret-key-change-in-production'
CORS(app)

# Initialize chatbot (will be loaded on first request)
chatbot = None
KB_PATH = 'data/knowledge_base'
DB_PATH = 'data/scraped/government_data.db'


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


@app.route('/')
def index():
    """Render main chat interface"""
    # Initialize session ID if not exists
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
    
    return render_template('index.html')


@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat messages"""
    try:
        data = request.get_json()
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return jsonify({
                'success': False,
                'error': 'Empty message'
            }), 400
        
        # Get chatbot
        bot = get_chatbot()
        if bot is None:
            return jsonify({
                'success': False,
                'error': 'Chatbot not initialized. Please run setup first.'
            }), 500
        
        # Process message
        response = bot.chat(user_message)
        
        return jsonify({
            'success': True,
            'response': response['text'],
            'type': response['type'],
            'language': response['language'],
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
        'embedding_dimension': bot.embedding_generator.embedding_dimension
    })


if __name__ == '__main__':
    print("\n" + "="*60)
    print("Government Services Chatbot - Web Interface")
    print("="*60 + "\n")
    
    # Check if knowledge base exists
    if not os.path.exists(KB_PATH):
        print("❌ Error: Knowledge base not found!")
        print("\nPlease run these steps first:")
        print("  1. python data_collection/static_data.py")
        print("  2. python knowledge_base/build_index.py")
        print("\n" + "="*60 + "\n")
        sys.exit(1)
    
    print("✓ Knowledge base found")
    print("✓ Starting web server...")
    print("\n" + "="*60)
    print("Server running at: http://localhost:5000")
    print("Press Ctrl+C to stop")
    print("="*60 + "\n")
    
    # Run Flask app
    app.run(host='0.0.0.0', port=5000, debug=True)
