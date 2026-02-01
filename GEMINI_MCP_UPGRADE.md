# 🚀 Upgrading to Gemini with MCP Integration

Guide to enhance the chatbot with Google Gemini API and Model Context Protocol (MCP) for TN e-Sevai services.

---

## 🎯 What You'll Get

### Current Setup (Local Only):
- ✅ Completely private
- ✅ No API costs
- ❌ Limited conversational ability
- ❌ Fixed responses

### With Gemini + MCP:
- ✅ Natural, human-like conversations
- ✅ Dynamic responses
- ✅ Better understanding of complex queries
- ✅ Real-time TN e-Sevai data through MCP
- ❌ Requires internet
- ❌ API costs (Gemini has free tier)

---

## 📋 Prerequisites

1. **Google Gemini API Key** (Free tier available)
   - Go to: https://makersuite.google.com/app/apikey
   - Create a new API key
   
2. **Python packages:**
   ```bash
   pip install google-generativeai mcp python-dotenv
   ```

---

## 🔧 Step 1: Add Environment Variables

Create a `.env` file in project root:

```env
# Google Gemini API
GEMINI_API_KEY=your_gemini_api_key_here

# MCP Configuration
MCP_SERVER_URL=https://api.tnesevai.gov.in  # TN e-Sevai API endpoint
MCP_API_KEY=your_tnesevai_api_key  # If required
```

Add to `.gitignore`:
```
.env
```

---

## 🔨 Step 2: Create Gemini Integration

Create `nlp_engine/gemini_engine.py`:

```python
"""
Gemini API Integration
Provides natural language understanding and generation using Google Gemini
"""

import os
import google.generativeai as genai
from dotenv import load_dotenv
import logging

load_dotenv()
logger = logging.getLogger(__name__)


class GeminiChatbot:
    """Gemini-powered conversational engine"""
    
    def __init__(self):
        # Configure Gemini
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in .env file")
        
        genai.configure(api_key=api_key)
        
        # Initialize model
        self.model = genai.GenerativeModel('gemini-pro')
        
        # System prompt for TN Government services
        self.system_prompt = """You are a helpful assistant for Tamil Nadu Government services.
        
Your role:
- Help users navigate TN government websites
- Provide information about government certificates and services
- Answer in the user's language (Tamil or English)
- Be concise and factual
- Always provide official website links and contact numbers

Available services:
1. Birth Certificate (பிறப்பு சான்றிதழ்)
2. Income Certificate (வருமான சான்றிதழ்)
3. Community Certificate (சமூக சான்றிதழ்)
4. Ration Card (ரேஷன் அட்டை)

Website: https://www.tnedistrict.gov.in
Helpline: 1800-425-1000
"""
        
        logger.info("✓ Gemini chatbot initialized")
    
    def chat(self, user_message: str, context: dict = None) -> dict:
        """
        Send message to Gemini and get response
        
        Args:
            user_message: User's question
            context: Previous conversation context
            
        Returns:
            Response dictionary with text and metadata
        """
        try:
            # Build full prompt with context
            full_prompt = f"{self.system_prompt}\n\nUser: {user_message}\n\nAssistant:"
            
            # Add context if available
            if context and context.get('last_service'):
                full_prompt = f"Previous topic: {context['last_service']}\n\n" + full_prompt
            
            # Generate response
            response = self.model.generate_content(full_prompt)
            
            return {
                'text': response.text,
                'type': 'gemini_response',
                'success': True
            }
            
        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            return {
                'text': "Sorry, I'm having trouble connecting. Please try again.",
                'type': 'error',
                'success': False,
                'error': str(e)
            }


# Test function
if __name__ == '__main__':
    bot = GeminiChatbot()
    
    # Test in English
    response = bot.chat("How to apply for birth certificate?")
    print("English:", response['text'])
    
    # Test in Tamil
    response = bot.chat("பிறப்பு சான்றிதழ் எப்படி பெறுவது?")
    print("Tamil:", response['text'])
```

---

## 🌐 Step 3: Create MCP Server for TN e-Sevai

Create `mcp_server/tnesevai_mcp.py`:

```python
"""
Model Context Protocol (MCP) Server for TN e-Sevai
Provides real-time access to TN government services data
"""

import os
import json
import requests
from typing import Dict, List
from dotenv import load_dotenv
import logging

load_dotenv()
logger = logging.getLogger(__name__)


class TNeSevaiMCP:
    """MCP server for TN e-Sevai government services"""
    
    def __init__(self):
        self.base_url = os.getenv('MCP_SERVER_URL', 'https://api.tnesevai.gov.in')
        self.api_key = os.getenv('MCP_API_KEY', '')
        
        # MCP tools/functions that Gemini can call
        self.tools = [
            {
                "name": "get_certificate_status",
                "description": "Check the status of a certificate application",
                "parameters": {
                    "application_number": "string",
                    "certificate_type": "string (birth/income/community/ration)"
                }
            },
            {
                "name": "get_service_info",
                "description": "Get detailed information about a government service",
                "parameters": {
                    "service_type": "string (birth_certificate/income_certificate/etc)"
                }
            },
            {
                "name": "find_nearest_sevai_center",
                "description": "Find nearest e-Sevai center based on location",
                "parameters": {
                    "pincode": "string",
                    "district": "string"
                }
            },
            {
                "name": "get_required_documents",
                "description": "Get list of required documents for a service",
                "parameters": {
                    "service_type": "string"
                }
            }
        ]
        
        logger.info("✓ TN e-Sevai MCP server initialized")
    
    def get_certificate_status(self, application_number: str, certificate_type: str) -> Dict:
        """
        Check certificate application status
        
        In production, this would call the actual TN e-Sevai API
        For now, returns mock data
        """
        # Mock response (replace with actual API call)
        return {
            "application_number": application_number,
            "certificate_type": certificate_type,
            "status": "Under Verification",
            "submitted_date": "2026-01-20",
            "expected_completion": "2026-02-05",
            "current_stage": "Document Verification at Tahsildar Office",
            "tracking_url": f"https://www.tnedistrict.gov.in/track/{application_number}"
        }
    
    def get_service_info(self, service_type: str) -> Dict:
        """Get detailed service information from local knowledge base"""
        from data_collection.static_data import GOVERNMENT_SERVICES_DATA
        
        for service in GOVERNMENT_SERVICES_DATA['services']:
            if service['id'] == service_type:
                return service
        
        return {"error": "Service not found"}
    
    def find_nearest_sevai_center(self, pincode: str = None, district: str = None) -> List[Dict]:
        """Find nearest e-Sevai centers"""
        # Mock data (replace with actual API)
        return [
            {
                "name": "Chennai Corporation e-Sevai Center",
                "address": "Ripon Building, Chennai - 600003",
                "phone": "044-2538-4520",
                "timings": "9:00 AM - 5:00 PM",
                "services": ["Birth Certificate", "Income Certificate"]
            },
            {
                "name": "Taluk Office e-Sevai",
                "address": "Anna Salai, Chennai - 600002",
                "phone": "044-2859-4122",
                "timings": "10:00 AM - 5:00 PM",
                "services": ["All Certificates"]
            }
        ]
    
    def get_required_documents(self, service_type: str) -> List[str]:
        """Get required documents list"""
        service = self.get_service_info(service_type)
        if 'requirements' in service:
            return service['requirements']
        return []
    
    def execute_tool(self, tool_name: str, parameters: Dict) -> Dict:
        """Execute MCP tool and return result"""
        if tool_name == "get_certificate_status":
            return self.get_certificate_status(**parameters)
        elif tool_name == "get_service_info":
            return self.get_service_info(**parameters)
        elif tool_name == "find_nearest_sevai_center":
            return self.find_nearest_sevai_center(**parameters)
        elif tool_name == "get_required_documents":
            return self.get_required_documents(**parameters)
        else:
            return {"error": f"Unknown tool: {tool_name}"}


# Test
if __name__ == '__main__':
    mcp = TNeSevaiMCP()
    
    # Test status check
    status = mcp.get_certificate_status("TN202601001234", "birth_certificate")
    print("Status:", json.dumps(status, indent=2))
    
    # Test finding centers
    centers = mcp.find_nearest_sevai_center(district="Chennai")
    print("\nCenters:", json.dumps(centers, indent=2))
```

---

## 🔗 Step 4: Connect Gemini + MCP

Create `chatbot_engine/gemini_mcp_chatbot.py`:

```python
"""
Enhanced Chatbot with Gemini + MCP Integration
Combines Gemini's conversational ability with real-time TN e-Sevai data
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from nlp_engine.gemini_engine import GeminiChatbot
from mcp_server.tnesevai_mcp import TNeSevaiMCP
from nlp_engine.text_processor import BilingualNLPEngine
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EnhancedGeminiMCPChatbot:
    """
    Advanced chatbot combining:
    - Gemini: Natural language understanding
    - MCP: Real-time government data access
    - Local NLP: Language detection and preprocessing
    """
    
    def __init__(self):
        logger.info("Initializing Enhanced Gemini + MCP Chatbot...")
        
        # Initialize components
        self.gemini = GeminiChatbot()
        self.mcp = TNeSevaiMCP()
        self.nlp = BilingualNLPEngine()
        
        # Conversation context
        self.context = {
            'history': [],
            'last_service': None,
            'last_query_type': None
        }
        
        logger.info("✓ Enhanced chatbot ready!")
    
    def chat(self, user_message: str) -> dict:
        """
        Process user message with Gemini + MCP
        
        Args:
            user_message: User's question
            
        Returns:
            Response with text and metadata
        """
        # Analyze query
        analysis = self.nlp.analyze_query(user_message)
        logger.info(f"Query analysis: {analysis['intent']} | {analysis['service_type']}")
        
        # Check if we need MCP data
        mcp_data = None
        if 'status' in analysis['intent']:
            # User asking about status - need MCP
            mcp_data = self.mcp.get_certificate_status(
                application_number="AUTO_EXTRACT",  # You'd extract from message
                certificate_type=analysis['service_type']
            )
        elif 'documents' in analysis['intent']:
            # User asking about documents
            mcp_data = self.mcp.get_required_documents(
                service_type=f"{analysis['service_type']}_certificate"
            )
        elif 'center' in user_message.lower() or 'office' in user_message.lower():
            # Looking for e-Sevai center
            mcp_data = self.mcp.find_nearest_sevai_center()
        
        # Build enhanced prompt for Gemini
        if mcp_data:
            enhanced_message = f"{user_message}\n\n[Real-time data: {json.dumps(mcp_data)}]"
        else:
            enhanced_message = user_message
        
        # Get Gemini response
        response = self.gemini.chat(enhanced_message, self.context)
        
        # Update context
        self.context['history'].append({
            'user': user_message,
            'bot': response['text']
        })
        self.context['last_service'] = analysis['service_type']
        self.context['last_query_type'] = analysis['intent']
        
        return {
            'text': response['text'],
            'type': 'enhanced_response',
            'language': analysis['language'],
            'intent': analysis['intent'],
            'mcp_data_used': mcp_data is not None
        }


# Test
if __name__ == '__main__':
    bot = EnhancedGeminiMCPChatbot()
    
    print("=== Gemini + MCP Chatbot Test ===\n")
    
    # Test 1: General query
    response = bot.chat("How to apply for birth certificate?")
    print(f"Q: How to apply for birth certificate?")
    print(f"A: {response['text']}\n")
    
    # Test 2: Status check (uses MCP)
    response = bot.chat("Check status of application TN202601001234")
    print(f"Q: Check status of application")
    print(f"A: {response['text']}")
    print(f"MCP used: {response['mcp_data_used']}\n")
```

---

## 🔄 Step 5: Update app.py

Modify `app.py` to use new Gemini+MCP chatbot:

```python
# Add at top
import os
from dotenv import load_dotenv

load_dotenv()

# Replace chatbot initialization
USE_GEMINI = os.getenv('USE_GEMINI', 'false').lower() == 'true'

if USE_GEMINI:
    from chatbot_engine.gemini_mcp_chatbot import EnhancedGeminiMCPChatbot
    chatbot_instance = EnhancedGeminiMCPChatbot()
    print("✓ Using Gemini + MCP Enhanced Mode")
else:
    from chatbot_engine.chatbot import GovernmentChatbot
    chatbot_instance = GovernmentChatbot(
        knowledge_base_path='./data/knowledge_base',
        db_path='./data/scraped/government_data.db'
    )
    print("✓ Using Local Mode")
```

---

## 📦 Step 6: Update requirements.txt

Add new dependencies:

```txt
# Existing packages...

# Gemini Integration
google-generativeai>=0.3.0
python-dotenv>=1.0.0

# MCP (if using official MCP library)
mcp>=1.0.0
```

---

## 🚀 Step 7: Usage

### Option A: Local Mode (Current)
```bash
python app.py
```

### Option B: Gemini + MCP Mode
```bash
# Set in .env file
USE_GEMINI=true

# Or set environment variable
set USE_GEMINI=true  # Windows
export USE_GEMINI=true  # Mac/Linux

python app.py
```

---

## 💡 Advantages of Gemini + MCP

### Better Conversations:
❌ **Before:** "Birth Certificate. Documents: Aadhaar, Hospital certificate..."
✅ **After:** "Sure! To apply for a birth certificate, you'll need a few documents. Let me walk you through this..."

### Real-time Data:
❌ **Before:** Generic information only
✅ **After:** "Your application TN202601001234 is currently under verification at the Tahsildar office. Expected completion: Feb 5, 2026"

### Contextual Understanding:
❌ **Before:** Treats each question independently
✅ **After:** Remembers conversation, understands follow-up questions

---

## 💰 Cost Considerations

### Gemini API Pricing (as of 2026):
- **Free Tier:** 60 requests/minute
- **Paid:** ~$0.001 per request
- **For personal use:** Free tier is enough

### MCP:
- If TN e-Sevai provides API: Check their pricing
- Self-hosted: No additional cost

---

## 🔒 Security Notes

1. **Never commit .env file** (already in .gitignore)
2. **Keep API keys secret**
3. **Use environment variables in production**
4. **Rate limit API calls** to avoid abuse

---

## 🧪 Testing

```bash
# Test Gemini integration
python nlp_engine/gemini_engine.py

# Test MCP server
python mcp_server/tnesevai_mcp.py

# Test combined chatbot
python chatbot_engine/gemini_mcp_chatbot.py
```

---

## 📝 Summary

**Files to create:**
1. `.env` - API keys
2. `nlp_engine/gemini_engine.py` - Gemini integration
3. `mcp_server/tnesevai_mcp.py` - MCP server
4. `chatbot_engine/gemini_mcp_chatbot.py` - Combined chatbot

**Files to modify:**
1. `app.py` - Add USE_GEMINI toggle
2. `requirements.txt` - Add dependencies
3. `.gitignore` - Add .env

**Benefits:**
- ✅ Natural conversations
- ✅ Real-time data
- ✅ Context awareness
- ✅ Multilingual (Tamil + English)
- ✅ Still works offline (fallback to local mode)

---

Need help implementing this? Let me know! 🚀
