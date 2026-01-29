// Popup script

document.getElementById('openChat').addEventListener('click', () => {
  // Get current tab and send message to content script
  chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
    chrome.tabs.sendMessage(tabs[0].id, { action: 'openChat' });
    window.close();
  });
});
