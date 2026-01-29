# How to Upload to GitHub

## The Error You're Seeing

The error "Unable to connect to the server" means the Flask server isn't running. The chatbot extension needs the server to be active.

## Solution: Keep Server Running

**Before using the extension, always run:**

```powershell
cd C:\Users\Asus\OneDrive\Desktop\chat
.\venv\Scripts\activate
python app.py
```

**Keep this terminal window open** while using the extension!

---

## Upload to GitHub

### Step 1: Create GitHub Repository

1. Go to https://github.com
2. Click "New repository"
3. Name it: `tn-govt-chatbot`
4. Don't initialize with README (we already have one)
5. Click "Create repository"

### Step 2: Push Code (After Git Installs)

After Git installation completes, **restart PowerShell** then run:

```powershell
cd C:\Users\Asus\OneDrive\Desktop\chat

# Initialize git
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit: TN Govt Chatbot with browser extension"

# Add your GitHub repository
git remote add origin https://github.com/YOUR_USERNAME/tn-govt-chatbot.git

# Push to GitHub
git branch -M main
git push -u origin main
```

Replace `YOUR_USERNAME` with your actual GitHub username.

### Step 3: If Git Asks for Authentication

```powershell
# Set your name and email
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

Then try pushing again.

---

## ✅ Checklist Before Using Extension

1. ✓ Server running (`python app.py`)
2. ✓ Extension installed in browser
3. ✓ Visit a TN government website
4. ✓ See green floating button
5. ✓ Click and chat!

## 🔧 If Extension Still Shows Error

1. Check server is running at http://localhost:5000
2. Reload the extension: `chrome://extensions/` → Click reload
3. Refresh the government website page
4. Try again

---

## 📁 What Gets Uploaded to GitHub

✅ Source code (Python files)
✅ Browser extension files
✅ Configuration files
✅ README and documentation
✅ requirements.txt
✅ Database and knowledge base files

❌ Virtual environment (venv/) - excluded
❌ Cache files - excluded
❌ IDE files - excluded
