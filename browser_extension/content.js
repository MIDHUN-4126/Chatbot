// Content script - Injects the floating chat widget into every webpage

// State Management
let state = {
  isOpen: false,
  messages: [],
  user: null,
  position: { bottom: '20px', right: '20px', top: 'auto', left: 'auto' }
};

// Initialize
async function init() {
  await loadState();
  if (!document.getElementById('tn-govt-chatbot-widget')) {
    createChatWidget();
    applyState();
  }
  
  // Try to auto-detect user if not logged in
  if (!state.user) {
    startUserDetection();
  }
}

// State Management with chrome.storage.local for cross-origin persistence
function loadState() {
  return new Promise((resolve) => {
    chrome.storage.local.get(['tnChatbotState', 'sessionTag'], (result) => {
      // Check if this is a new browser session (using sessionStorage as a session marker)
      const currentSessionTag = sessionStorage.getItem('tn-session-tag');
      
      if (result.tnChatbotState) {
        state = result.tnChatbotState;
        
        // If we have state but no session tag in this tab, it might be a new tab or restore.
        // User wanted: "only fade when the user is loged out or whenever i close and open the chrome"
        // chrome.storage.local persists forever. To emulate "session" lifetime across domains:
        // We can't easily detect "browser close" reliably for extension storage cleanup.
        // However, using local storage solves the "redirect" issue which is more critical.
      }
      resolve();
    });
  });
}

function saveState() {
  chrome.storage.local.set({ 'tnChatbotState': state });
}

function startUserDetection() {
    // Run immediately
    if (detectUserOnPage()) return;

    // Observe changes for dynamic headers
    const observer = new MutationObserver((mutations) => {
        if (state.user) {
            observer.disconnect();
            return;
        }
        if (detectUserOnPage()) {
            observer.disconnect();
        }
    });

    observer.observe(document.body, { childList: true, subtree: true });

    // Stop observing after 5 seconds and use Guest fallback
    setTimeout(() => {
        observer.disconnect();
        if (!state.user) {
            console.log('User not detected, using Guest');
            handleLogin('Guest', true);
        }
    }, 5000);
}

function detectUserOnPage() {
    // 1. Common ID/Class patterns for Government portals
    const selectors = [
        '#lblUserID', '#lblUserName', '#userName', '.user-name', '.profile-name', 
        'span[id*="user"]', 'span[class*="user"]', '#welcomeUser',
        '.header-user', '.login-name', 'a[href*="profile"]', '.logged-in-user'
    ];

    for (const selector of selectors) {
        const el = document.querySelector(selector);
        if (el && el.innerText.trim().length > 2) {
             const name = cleanName(el.innerText);
             if(name && !name.includes('Log')) {
                 console.log("Found user via selector:", name);
                 handleLogin(name, true); 
                 return true;
             }
        }
    }

    // 2. Heuristic: Look for elements near Logout/Sign Out/Power Icon
    const iconButtons = document.querySelectorAll('i, svg, img, a, button, .fa, .fas, .material-icons');
    for (const btn of iconButtons) {
        let text = btn.innerText || btn.title || btn.getAttribute('aria-label') || '';
        const classList = btn.className.toString().toLowerCase();
        
        // Detect logout button by text or icon class
        const isLogout = 
            text.toLowerCase().includes('logout') || 
            text.toLowerCase().includes('sign out') || 
            classList.includes('power') || 
            classList.includes('logout') || 
            classList.includes('sign-out');

        if (isLogout) {
            // Check previous sibling or parent container text
            // Strategy: Go up to a container (like a header row), and look for text nodes
            let container = btn.parentElement;
            
            // Try 3 levels up
            for(let i=0; i<3; i++) { 
                if (!container) break;

                // Clone and remove the logout button text to see what remains
                const clone = container.cloneNode(true);
                // Remove the logout button element from clone to avoid reading "Logout" as name
                const btnInClone = clone.querySelector('.' + btn.className.split(' ').join('.'));
                if(btnInClone) btnInClone.remove();

                const containerText = clone.innerText.trim();
                
                // Split by newlines to get separate visual blocks
                const lines = containerText.split('\n').map(l => l.trim()).filter(l => l.length > 2);
                
                for (const line of lines) {
                    const cleaned = cleanName(line);
                    // Filter noise
                    if (cleaned && 
                        cleaned.length < 30 && 
                        !cleaned.toLowerCase().includes('setting') && 
                        !cleaned.toLowerCase().includes('english') &&
                        !cleaned.toLowerCase().includes('tamil') &&
                        !cleaned.toLowerCase().match(/^(home|help|admin|user)$/)) {
                        
                        console.log("Found user near logout:", cleaned);
                        handleLogin(cleaned, true);
                        return true;
                    }
                }
                container = container.parentElement;
            }
        }
    }
    return false;
}

function cleanName(text) {
    // Remove "Welcome", "Hello", etc.
    return text.replace(/welcome|hello|hi|mr\.|ms\.|user:/gi, '').trim();
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
  
  // Login View (hidden - auto-detection only)
  const loginView = `
    <div id="tn-chatbot-login" class="tn-chatbot-login-view tn-chatbot-hidden-view">
      <div class="tn-chatbot-login-icon">🔍</div>
      <div class="tn-chatbot-login-title">Detecting user...</div>
    </div>
  `;

  // Chat View
  const chatView = `
    <div class="tn-chatbot-header" id="tn-chatbot-header">
      <div class="tn-chatbot-header-content">
        <div class="tn-chatbot-avatar">
          <img src="${chrome.runtime.getURL('icons/icon-48.png')}" alt="TN Logo" style="width: 100%; height: 100%; object-fit: contain;">
        </div>
        <div class="tn-chatbot-title">
          <div class="tn-chatbot-name">TN Govt Assistant</div>
          <div class="tn-chatbot-status">
            <span class="tn-status-dot"></span> <span id="tn-user-display">${state.user || 'Online'}</span>
          </div>
        </div>
      </div>
      <div class="tn-chatbot-header-controls">
        <button class="tn-chatbot-logout" id="tn-chatbot-logout-btn" title="Logout">↩</button>
        <button class="tn-chatbot-close" id="tn-chatbot-close-btn">✕</button>
      </div>
    </div>
    
    <div class="tn-chatbot-messages" id="tn-chatbot-messages">
      <!-- Messages injected here -->
    </div>
    
    <div class="tn-image-preview-container" id="tn-image-preview">
        <!-- Image preview will appear here -->
    </div>

    <div class="tn-chatbot-input-container">
      <div class="tn-chatbot-typing" id="tn-typing-indicator" style="display: none;">
        <span></span><span></span><span></span>
      </div>
      <input 
        type="text" 
        class="tn-chatbot-input" 
        id="tn-chatbot-input"
        placeholder="Type your question... (Paste images supported)"
        autocomplete="off"
      />
      <button class="tn-chatbot-send" id="tn-chatbot-send-btn">
        <svg viewBox="0 0 24 24" fill="currentColor" width="20" height="20">
          <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/>
        </svg>
      </button>
    </div>
  `;

  chatContainer.innerHTML = loginView + chatView;
  
  // Append to body
  document.body.appendChild(floatingBtn);
  document.body.appendChild(chatContainer);
  
  // Make Draggable
  makeDraggable(chatContainer);

  // Event listeners
  floatingBtn.addEventListener('click', toggleChat);
  document.getElementById('tn-chatbot-close-btn').addEventListener('click', toggleChat);
  document.getElementById('tn-chatbot-send-btn').addEventListener('click', sendMessage);
  
  const inputEl = document.getElementById('tn-chatbot-input');
  inputEl.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') sendMessage();
  });
  
  // Paste listener for images
  inputEl.addEventListener('paste', handlePaste);

  // Logout listener
  document.getElementById('tn-chatbot-logout-btn').addEventListener('click', handleLogout);
}

function makeDraggable(element) {
  const header = element.querySelector('.tn-chatbot-header');
  const loginView = element.querySelector('#tn-chatbot-login');

  let isDragging = false;
  let startX;
  let startY;
  let initialLeft;
  let initialTop;

  // Handler for both header and login view
  function dragStart(e) {
    if (e.target.closest('button') || e.target.closest('input')) return;
    
    // If not header and not login view (e.g. messages area), don't drag
    if (!e.target.closest('.tn-chatbot-header') && !e.target.closest('#tn-chatbot-login')) return;

    // Use a flag to prevent text selection while dragging
    document.body.style.userSelect = 'none';
    
    initialLeft = element.offsetLeft;
    initialTop = element.offsetTop;
    startX = e.clientX;
    startY = e.clientY;
    
    isDragging = true;
    
    document.addEventListener('mousemove', drag);
    document.addEventListener('mouseup', dragEnd);
  }

  function drag(e) {
    if (!isDragging) return;
    
    e.preventDefault();
    const currentX = e.clientX - startX;
    const currentY = e.clientY - startY;

    const newLeft = initialLeft + currentX;
    const newTop = initialTop + currentY;

    // Boundary checks
    const maxLeft = window.innerWidth - element.offsetWidth;
    const maxTop = window.innerHeight - element.offsetHeight;

    element.style.left = `${Math.min(Math.max(0, newLeft), maxLeft)}px`;
    element.style.top = `${Math.min(Math.max(0, newTop), maxTop)}px`;
    element.style.bottom = 'auto';
    element.style.right = 'auto';
  }

  function dragEnd() {
    isDragging = false;
    document.body.style.userSelect = ''; // Restore selection
    document.removeEventListener('mousemove', drag);
    document.removeEventListener('mouseup', dragEnd);
    
    // Save position
    state.position = {
      top: element.style.top,
      left: element.style.left,
      bottom: 'auto',
      right: 'auto'
    };
    saveState();
  }

  // Attach listeners
  if (header) header.addEventListener('mousedown', dragStart);
  if (loginView) loginView.addEventListener('mousedown', dragStart);
}

function handleLogin(nameInput, isAuto = false) {
  let name = nameInput || 'Guest';

  if (name) {
    state.user = name;
    
    // UI Updates
    const loginView = document.getElementById('tn-chatbot-login');
    if (loginView) loginView.classList.add('tn-chatbot-hidden-view');
    
    const display = document.getElementById('tn-user-display');
    if (display) display.textContent = name;
    
    // No welcome message for auto-login to avoid spamming
    // User will see their name in the status bar
    
    saveState();
  }
}

function handleLogout() {
  state.user = null;
  state.messages = [];
  document.getElementById('tn-chatbot-messages').innerHTML = ''; // Clear DOM messages
  
  // Clear storage
  chrome.storage.local.remove('tnChatbotState');
  
  state.isOpen = true; // Keep widget open
  saveState();
  
  // Restart user detection
  startUserDetection();
}

function applyState() {
  const widget = document.getElementById('tn-govt-chatbot-widget');
  const btn = document.getElementById('tn-govt-chatbot-btn');
  
  // Apply position
  if (state.position.top !== 'auto') {
    widget.style.top = state.position.top;
    widget.style.left = state.position.left;
    widget.style.bottom = 'auto';
    widget.style.right = 'auto';
  }

  // Apply visibility
  if (state.isOpen) {
    widget.classList.remove('tn-chatbot-hidden');
    widget.classList.add('tn-chatbot-visible');
    btn.style.display = 'none';
  }

  // Restore messages
  if (state.messages.length > 0) {
    const messagesContainer = document.getElementById('tn-chatbot-messages');
    messagesContainer.innerHTML = ''; // Clear default
    state.messages.forEach(msg => {
       renderMessageToDOM(msg.text, msg.sender === 'user', msg.image);
    });
  } else if (state.user && state.messages.length === 0) {
    // Show welcome message for new users
    showWelcomeMessage();
  }
}

function showWelcomeMessage() {
  const welcomeText = `👋 <strong>Welcome ${state.user}!</strong>

I'm your Tamil Nadu Government Services Assistant. I can help you with:

<span style="font-size: 15px;">• 🏛️ Government service information</span>
<span style="font-size: 15px;">• 📄 Application procedures</span>
<span style="font-size: 15px;">• 💰 Fee details and payment methods</span>
<span style="font-size: 15px;">• 📋 Required documents</span>
<span style="font-size: 15px;">• 📞 Contact information</span>
<span style="font-size: 15px;">• ⏰ Office timings</span>

Feel free to ask me anything in <strong>Tamil</strong> or <strong>English</strong>!`;

  renderMessageToDOM(welcomeText, false);
  state.messages.push({ sender: 'bot', text: welcomeText });
  saveState();
}

let pendingImage = null; // Ephemeral state for image pending send

function handlePaste(e) {
  const items = (e.clipboardData || e.originalEvent.clipboardData).items;
  
  for (let index in items) {
    const item = items[index];
    if (item.kind === 'file' && item.type.includes('image/')) {
      const blob = item.getAsFile();
      const reader = new FileReader();
      
      reader.onload = function(event) {
        pendingImage = event.target.result;
        showImagePreview(pendingImage);
      };
      
      reader.readAsDataURL(blob);
      e.preventDefault(); // Prevent pasting the binary code if it tries to
    }
  }
}

function showImagePreview(base64Image) {
  const container = document.getElementById('tn-image-preview');
  container.innerHTML = `
    <img src="${base64Image}" class="tn-preview-image" />
    <button class="tn-preview-close" id="tn-clear-image">✕</button>
  `;
  container.classList.add('has-image');
  
  document.getElementById('tn-clear-image').addEventListener('click', () => {
    pendingImage = null;
    container.classList.remove('has-image');
    container.innerHTML = '';
  });
}

function toggleChat() {
  const widget = document.getElementById('tn-govt-chatbot-widget');
  const btn = document.getElementById('tn-govt-chatbot-btn');
  
  if (widget.classList.contains('tn-chatbot-hidden')) {
    widget.classList.remove('tn-chatbot-hidden');
    widget.classList.add('tn-chatbot-visible');
    btn.style.display = 'none';
    state.isOpen = true;
  } else {
    widget.classList.remove('tn-chatbot-visible');
    widget.classList.add('tn-chatbot-hidden');
    btn.style.display = 'flex';
    state.isOpen = false;
  }
  saveState();
}

async function sendMessage() {
  if (!state.user) return; // Guard logic if input somehow visible

  const input = document.getElementById('tn-chatbot-input');
  const message = input.value.trim();
  
  if (!message && !pendingImage) return;
  
  // Add user message with image if present
  addMessage(message, true, pendingImage);
  
  const currentImage = pendingImage; // Capture for sending
  
  // Clear input
  input.value = '';
  pendingImage = null;
  document.getElementById('tn-image-preview').classList.remove('has-image');
  document.getElementById('tn-image-preview').innerHTML = '';
  
  // Show typing indicator
  showTyping(true);
  
  try {
    // Get page context
    const pageContent = document.body.innerText;

    // Send to backend
    const response = await fetch('http://localhost:5000/api/chat', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ 
        message,
        image: currentImage, // Send base64 image
        page_content: pageContent,
        user_name: state.user
      })
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
    addErrorMessage('⚠️ Unable to connect to the server. Please ensure the chatbot server is running at <a href="http://localhost:5000" target="_blank">http://localhost:5000</a>');
    console.error('Error:', error);
  }
}

function addMessage(text, isUser, image = null) {
  // Update State
  state.messages.push({ sender: isUser ? 'user' : 'bot', text, image });
  saveState();
  
  renderMessageToDOM(text, isUser, image);
}

function addErrorMessage(htmlText) {
  const messagesContainer = document.getElementById('tn-chatbot-messages');
  if (!messagesContainer) return;

  const messageDiv = document.createElement('div');
  messageDiv.className = 'tn-message tn-bot-message tn-error-message';
  messageDiv.innerHTML = `
    <div class="tn-message-avatar">⚠️</div>
    <div class="tn-message-content">${htmlText}</div>
  `;
  
  messagesContainer.appendChild(messageDiv);
  messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

function renderMessageToDOM(text, isUser, image = null) {
  const messagesContainer = document.getElementById('tn-chatbot-messages');
  
  if (!messagesContainer) return; // Guard event loop

  const messageDiv = document.createElement('div');
  messageDiv.className = `tn-message ${isUser ? 'tn-user-message' : 'tn-bot-message'}`;
  
  let content = '';
  if (image) {
      content += `<img src="${image}" class="tn-message-image" />`;
  }
  if (text) {
      content += isUser ? `<div>${escapeHtml(text)}</div>` : formatBotMessage(text);
  }

  if (isUser) {
    messageDiv.innerHTML = `
      <div class="tn-message-content">${content}</div>
      <div class="tn-message-avatar">👤</div>
    `;
  } else {
    messageDiv.innerHTML = `
      <div class="tn-message-avatar">🤖</div>
      <div class="tn-message-content">${content}</div>
    `;
  }
  
  messagesContainer.appendChild(messageDiv);
  messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

function formatBotMessage(text) {
  // Check if text already contains HTML tags (for pre-formatted messages like welcome)
  const hasHTML = /<[^>]+>/.test(text);
  
  if (hasHTML) {
    // Already formatted, just process it
    let formatted = text.replace(/\n/g, '<br>');
    // Convert span-wrapped bullets into proper list items
    formatted = formatted.replace(/<span style="font-size: 15px;">(.*?)<\/span>/g, '<div style="padding: 4px 0;">$1</div>');
    return `<div style="line-height: 1.8;">${formatted}</div>`;
  }
  
  // Convert line breaks to <br>
  let formatted = escapeHtml(text).replace(/\n/g, '<br>');
  
  // Headers (### Text)
  formatted = formatted.replace(/###\s*(.*?)(<br>|$)/g, '<strong style="font-size: 16px; color: #00a000; display: block; margin: 8px 0;">$1</strong>$2');

  // Bold (**text**)
  formatted = formatted.replace(/\*\*(.*?)\*\*/g, '<strong style="color: #1e293b;">$1</strong>');
  
  // Bold (__text__)
  formatted = formatted.replace(/__(.*?)__/g, '<strong style="color: #1e293b;">$1</strong>');

  // Bullet points with custom styling
  formatted = formatted.replace(/•\s*/g, '<span style="color: #00a000; font-weight: bold; font-size: 18px; margin-right: 8px;">•</span>');
  
  // Links
  formatted = formatted.replace(/(https?:\/\/[^\s<]+)/g, '<a href="$1" target="_blank" style="color: #00a000; text-decoration: underline; font-weight: 500;">$1</a>');
  
  return `<div style="line-height: 1.8;">${formatted}</div>`;
}

function showTyping(show) {
  const indicator = document.getElementById('tn-typing-indicator');
  if (indicator) {
    indicator.style.display = show ? 'flex' : 'none';
  }
  
  if (show) {
    const messagesContainer = document.getElementById('tn-chatbot-messages');
    if (messagesContainer) {
      messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }
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

// Run Init
init();
