// Content script - Injects the floating chat widget into every webpage

// Check if widget already exists
if (!document.getElementById('tn-govt-chatbot-widget')) {
  createChatWidget();
}

function createChatWidget() {
  // Create floating button
  const floatingBtn = document.createElement('div');
  floatingBtn.id = 'tn-govt-chatbot-btn';
  floatingBtn.innerHTML = `
    <svg viewBox="0 0 24 24" fill="currentColor" width="32" height="32">
      <path d="M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm0 14H6l-2 2V4h16v12z"/>
      <path d="M7 9h2v2H7zm4 0h2v2h-2zm4 0h2v2h-2z"/>
    </svg>
  `;
  
  // Create chat container
  const chatContainer = document.createElement('div');
  chatContainer.id = 'tn-govt-chatbot-widget';
  chatContainer.className = 'tn-chatbot-hidden';
  chatContainer.innerHTML = `
    <div class="tn-chatbot-header">
      <div class="tn-chatbot-header-content">
        <div class="tn-chatbot-avatar">🏛️</div>
        <div class="tn-chatbot-title">
          <div class="tn-chatbot-name">TN Govt Assistant</div>
          <div class="tn-chatbot-status">
            <span class="tn-status-dot"></span> Online
          </div>
        </div>
      </div>
      <button class="tn-chatbot-close" id="tn-chatbot-close-btn">✕</button>
    </div>
    
    <div class="tn-chatbot-messages" id="tn-chatbot-messages">
      <div class="tn-message tn-bot-message">
        <div class="tn-message-avatar">🤖</div>
        <div class="tn-message-content">
          <strong>வணக்கம்! 🙏</strong><br><br>
          Hi! I'm your Tamil Nadu Government Services Assistant.<br><br>
          தமிழ்நாடு அரசு சேவைகள் தொடர்பாக நான் உங்களுக்கு உதவுகிறேன்.<br><br>
          Ask me about:<br>
          • பிறப்பு சான்றிதழ் (Birth Certificate)<br>
          • வருமான சான்றிதழ் (Income Certificate)<br>
          • சமூக சான்றிதழ் (Community Certificate)<br>
          • ரேஷன் அட்டை (Ration Card)<br><br>
          How can I help you today?
        </div>
      </div>
    </div>
    
    <div class="tn-chatbot-input-container">
      <div class="tn-chatbot-typing" id="tn-typing-indicator" style="display: none;">
        <span></span><span></span><span></span>
      </div>
      <input 
        type="text" 
        class="tn-chatbot-input" 
        id="tn-chatbot-input"
        placeholder="Type your question... (தமிழ் அல்லது English)"
        autocomplete="off"
      />
      <button class="tn-chatbot-send" id="tn-chatbot-send-btn">
        <svg viewBox="0 0 24 24" fill="currentColor" width="20" height="20">
          <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/>
        </svg>
      </button>
    </div>
  `;
  
  // Append to body
  document.body.appendChild(floatingBtn);
  document.body.appendChild(chatContainer);
  
  // Event listeners
  floatingBtn.addEventListener('click', toggleChat);
  document.getElementById('tn-chatbot-close-btn').addEventListener('click', toggleChat);
  document.getElementById('tn-chatbot-send-btn').addEventListener('click', sendMessage);
  document.getElementById('tn-chatbot-input').addEventListener('keypress', (e) => {
    if (e.key === 'Enter') sendMessage();
  });
}

function toggleChat() {
  const widget = document.getElementById('tn-govt-chatbot-widget');
  const btn = document.getElementById('tn-govt-chatbot-btn');
  
  if (widget.classList.contains('tn-chatbot-hidden')) {
    widget.classList.remove('tn-chatbot-hidden');
    widget.classList.add('tn-chatbot-visible');
    btn.style.display = 'none';
  } else {
    widget.classList.remove('tn-chatbot-visible');
    widget.classList.add('tn-chatbot-hidden');
    btn.style.display = 'flex';
  }
}

async function sendMessage() {
  const input = document.getElementById('tn-chatbot-input');
  const message = input.value.trim();
  
  if (!message) return;
  
  // Add user message
  addMessage(message, true);
  input.value = '';
  
  // Show typing indicator
  showTyping(true);
  
  try {
    // Send to backend
    const response = await fetch('http://localhost:5000/api/chat', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ message })
    });
    
    const data = await response.json();
    
    showTyping(false);
    
    if (data.success) {
      addMessage(data.response, false);
    } else {
      addMessage('Sorry, I encountered an error. Please try again.', false);
    }
  } catch (error) {
    showTyping(false);
    addMessage('⚠️ Unable to connect to the server. Please ensure the chatbot server is running at http://localhost:5000', false);
    console.error('Error:', error);
  }
}

function addMessage(text, isUser) {
  const messagesContainer = document.getElementById('tn-chatbot-messages');
  
  const messageDiv = document.createElement('div');
  messageDiv.className = `tn-message ${isUser ? 'tn-user-message' : 'tn-bot-message'}`;
  
  if (isUser) {
    messageDiv.innerHTML = `
      <div class="tn-message-content">${escapeHtml(text)}</div>
      <div class="tn-message-avatar">👤</div>
    `;
  } else {
    messageDiv.innerHTML = `
      <div class="tn-message-avatar">🤖</div>
      <div class="tn-message-content">${formatBotMessage(text)}</div>
    `;
  }
  
  messagesContainer.appendChild(messageDiv);
  messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

function formatBotMessage(text) {
  // Convert line breaks to <br>
  let formatted = escapeHtml(text).replace(/\n/g, '<br>');
  
  // Make bold text (Markdown style: **text**)
  formatted = formatted.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');

  // Make emojis and bullets stand out
  formatted = formatted.replace(/•/g, '<span style="color: #667eea;">•</span>');
  
  // Make headers bold
  formatted = formatted.replace(/📋(.*?)(<br>|$)/g, '<strong>📋$1</strong>$2');
  formatted = formatted.replace(/📑(.*?)(<br>|$)/g, '<strong>📑$1</strong>$2');
  formatted = formatted.replace(/📝(.*?)(<br>|$)/g, '<strong>📝$1</strong>$2');
  formatted = formatted.replace(/💰(.*?)(<br>|$)/g, '<strong>💰$1</strong>$2');
  formatted = formatted.replace(/⏱️(.*?)(<br>|$)/g, '<strong>⏱️$1</strong>$2');
  formatted = formatted.replace(/📞(.*?)(<br>|$)/g, '<strong>📞$1</strong>$2');
  formatted = formatted.replace(/🌐(.*?)(<br>|$)/g, '<strong>🌐$1</strong>$2');
  
  return formatted;
}

function showTyping(show) {
  const indicator = document.getElementById('tn-typing-indicator');
  indicator.style.display = show ? 'flex' : 'none';
  
  if (show) {
    const messagesContainer = document.getElementById('tn-chatbot-messages');
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
  }
}

function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

// Listen for messages from background script
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'openChat') {
    const widget = document.getElementById('tn-govt-chatbot-widget');
    if (widget.classList.contains('tn-chatbot-hidden')) {
      toggleChat();
    }
  }
});
