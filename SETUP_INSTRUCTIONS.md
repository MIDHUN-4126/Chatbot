# 🚀 Setup Instructions for TN Government Chatbot

Complete guide for anyone who downloads this project from GitHub.

---

## 📋 Prerequisites

- **Python 3.8 or higher** - [Download Python](https://www.python.org/downloads/)
- **Google Chrome** or **Microsoft Edge** browser
- **Windows/Mac/Linux** - Works on all platforms

---

## 📥 Step 1: Download the Project

### Option A: Using Git (Recommended)
```bash
git clone https://github.com/MIDHUN-4126/Chatbot.git
cd Chatbot
```

### Option B: Download ZIP
1. Go to https://github.com/MIDHUN-4126/Chatbot
2. Click green "Code" button → "Download ZIP"
3. Extract the ZIP file
4. Open terminal/PowerShell in the extracted folder

---

## 🐍 Step 2: Setup Python Environment

### Windows:
```powershell
# Create virtual environment
python -m venv venv

# Activate it
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Mac/Linux:
```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

**This will install:**
- Flask (web server)
- scikit-learn (embeddings)
- langdetect (language detection)
- FAISS (vector search)
- Other dependencies

---

## 🗄️ Step 3: Build Knowledge Base

Run this command to create the knowledge base with government services data:

```bash
python knowledge_base/build_index.py
```

**Expected output:**
```
✓ Database created successfully
✓ 4 services inserted
✓ Knowledge base created at: ./data/knowledge_base
✓ Total documents indexed: 4
```

---

## 🖥️ Step 4: Start the Server

### Windows - Easy Way:
Double-click **`start_server.bat`**

### Windows - Command Line:
```powershell
.\venv\Scripts\activate
python app.py
```

### Mac/Linux:
```bash
source venv/bin/activate
python app.py
```

**Server will start at:** `http://localhost:5000`

**⚠️ IMPORTANT:** Keep this terminal window open while using the extension!

---

## 🌐 Step 5: Install Browser Extension

### For Chrome/Edge:

1. Open browser and go to:
   - **Chrome:** `chrome://extensions/`
   - **Edge:** `edge://extensions/`

2. Enable **"Developer mode"** (toggle in top-right corner)

3. Click **"Load unpacked"** button

4. Navigate to the downloaded project folder

5. Select the **`browser_extension`** folder

6. Extension installed! ✅

### You should see:
- Extension icon in your browser toolbar
- "TN Govt Assistant" extension card

---

## ✅ Step 6: Test It!

1. **Make sure server is running** (Step 4)

2. Visit any Tamil Nadu government website:
   - https://www.tn.gov.in
   - https://www.tnedistrict.gov.in
   - https://www.tnega.org
   - Or any other *.tn.gov.in site

3. Look for the **green floating chat button** in the bottom-right corner

4. Click it and start chatting! 🎉

### Try these questions:
- "How to apply for birth certificate?"
- "பிறப்பு சான்றிதழ் எப்படி பெறுவது?"
- "What documents needed for income certificate?"
- "Check ration card status"

---

## 🔧 Troubleshooting

### ❌ "Unable to connect to server" error

**Problem:** The Flask server isn't running

**Solution:** 
1. Open terminal/PowerShell
2. Navigate to project folder
3. Run: `python app.py`
4. Keep terminal open
5. Reload browser page

---

### ❌ Extension doesn't show up on website

**Problem:** You're on a non-government website

**Solution:** The extension only works on TN government domains (*.tn.gov.in, *.tnega.org, etc.) for privacy/security

---

### ❌ "Module not found" errors

**Problem:** Dependencies not installed

**Solution:**
```bash
pip install -r requirements.txt
```

---

### ❌ Knowledge base not found

**Problem:** Haven't built the index

**Solution:**
```bash
python knowledge_base/build_index.py
```

---

## 📁 Project Structure

```
Chatbot/
├── app.py                     # Start this file (Flask server)
├── start_server.bat          # Quick start (Windows)
├── requirements.txt          # Dependencies list
├── browser_extension/        # <- Select this folder in browser
│   ├── manifest.json
│   ├── content.js
│   ├── widget.css
│   └── ...
├── data/
│   ├── scraped/              # Auto-generated database
│   └── knowledge_base/       # Auto-generated index
└── ...
```

---

## 🎯 Daily Usage

### Every time you want to use the chatbot:

1. **Start the server:**
   - Windows: Double-click `start_server.bat`
   - Or run: `python app.py`

2. **Visit a TN govt website**

3. **Click the green chat button**

4. **Done!** Chat away 💬

### When finished:
- Press `Ctrl+C` in terminal to stop server
- Or just close the terminal window

---

## 🆕 Updating the Code

If the GitHub repository gets updated:

```bash
cd Chatbot
git pull origin main
pip install -r requirements.txt  # In case new dependencies added
```

---

## 📞 Need Help?

- **GitHub Issues:** https://github.com/MIDHUN-4126/Chatbot/issues
- **Check logs:** Look at the terminal where server is running
- **Reload extension:** Go to `chrome://extensions/` → Click reload button

---

## 🎨 Customization

### Change the color theme:
Edit `browser_extension/widget.css` - Look for color values like `#008000`

### Add more services:
Edit `data_collection/static_data.py` - Add new service entries

### Change server port:
Edit `config/config.yaml` - Change port number

---

## ⚠️ Important Notes

- **Server must be running** for extension to work
- Extension only works on TN government domains
- All processing happens locally (100% private)
- No internet required after initial setup
- Knowledge base persists - only build once

---

## ✅ Quick Checklist

Before asking for help, verify:

- [ ] Python 3.8+ installed
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Knowledge base built (`python knowledge_base/build_index.py`)
- [ ] Server running (`python app.py`)
- [ ] Extension loaded in browser (Developer mode ON)
- [ ] Visiting a TN government website
- [ ] Green button visible in bottom-right corner

---

**🎉 You're all set! Enjoy your private TN Government Services Chatbot!**
