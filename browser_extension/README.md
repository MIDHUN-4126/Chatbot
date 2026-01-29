# Tamil Nadu Government Assistant - Browser Extension

## Installation Instructions

### Step 1: Start the Backend Server

Before installing the extension, make sure the chatbot server is running:

```powershell
cd c:\Users\Asus\OneDrive\Desktop\chat
.\venv\Scripts\Activate.ps1
python app.py
```

The server should be running at http://localhost:5000

### Step 2: Install Extension in Chrome/Edge

1. **Open Extension Management:**
   - Chrome: Go to `chrome://extensions/`
   - Edge: Go to `edge://extensions/`

2. **Enable Developer Mode:**
   - Toggle the "Developer mode" switch in the top right corner

3. **Load the Extension:**
   - Click "Load unpacked"
   - Navigate to: `c:\Users\Asus\OneDrive\Desktop\chat\browser_extension`
   - Click "Select Folder"

4. **Done!** The extension icon should appear in your browser toolbar

### Step 3: Use the Extension

**Method 1: Floating Widget**
- Visit any website
- Look for the purple floating chat button in the bottom-right corner
- Click it to open the chat widget

**Method 2: Extension Icon**
- Click the extension icon in the toolbar
- Click "Open Chat Widget" button

## Features

✅ Appears on every website you visit
✅ Floating chat button in corner
✅ Beautiful popup interface
✅ Bilingual support (Tamil + English)
✅ Real-time responses
✅ Persistent across page navigation

## Troubleshooting

### Widget not appearing?
- Refresh the page after installing the extension
- Check if Developer Mode is enabled
- Check browser console for errors (F12)

### Can't connect to server?
- Ensure the backend is running: `python app.py`
- Check that the server is at http://localhost:5000
- Try opening http://localhost:5000 in a browser tab

### Extension not loading?
- Make sure you're selecting the `browser_extension` folder, not a subfolder
- Check that manifest.json exists in the folder
- Reload the extension in chrome://extensions/

## Creating Icons

The extension needs icons. Create these files in `browser_extension/icons/`:

- `icon16.png` (16x16 pixels)
- `icon48.png` (48x48 pixels)  
- `icon128.png` (128x128 pixels)

Or you can use emoji/text as placeholders until you create proper icons.

## Customization

Edit these files to customize:
- `widget.css` - Change colors, sizes, positions
- `content.js` - Modify widget behavior
- `manifest.json` - Change extension name, permissions

## Privacy

- All data stays local
- No external API calls (except to your localhost server)
- No tracking or analytics
- No data collection
