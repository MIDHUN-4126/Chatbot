// Background service worker for the extension

// Listen for extension icon click
chrome.action.onClicked.addListener((tab) => {
  // Send message to content script to open chat
  chrome.tabs.sendMessage(tab.id, { action: 'openChat' });
});

// Listen for installation
chrome.runtime.onInstalled.addListener(() => {
  console.log('Tamil Nadu Government Assistant installed successfully!');
});

// Keep service worker alive
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'ping') {
    sendResponse({ status: 'alive' });
  }
  return true;
});
