// Popup script

document.getElementById('openChat').addEventListener('click', () => {
  // Add visual feedback
  const button = document.getElementById('openChat');
  button.innerHTML = '<span>⏳ Opening...</span>';
  button.style.opacity = '0.7';
  
  // Get current tab and send message to content script
  chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
    chrome.tabs.sendMessage(tabs[0].id, { action: 'openChat' }, (response) => {
      // Close popup after a brief delay
      setTimeout(() => {
        window.close();
      }, 300);
    });
  });
});

// Add keyboard shortcut - Enter key
document.addEventListener('keydown', (e) => {
  if (e.key === 'Enter') {
    document.getElementById('openChat').click();
  }
});

// Add subtle entrance animation
window.addEventListener('load', () => {
  document.body.style.opacity = '0';
  setTimeout(() => {
    document.body.style.transition = 'opacity 0.3s ease';
    document.body.style.opacity = '1';
  }, 50);
});
