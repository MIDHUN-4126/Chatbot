@echo off
echo ============================================
echo TN Government Chatbot - GEMINI ENHANCED MODE
echo ============================================
echo.
echo This server uses Google Gemini API for
echo intelligent website navigation assistance
echo ============================================
echo.

cd /d %~dp0

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo Checking dependencies...
pip show google-generativeai >nul 2>&1
if errorlevel 1 (
    echo Installing google-generativeai package...
    pip install google-generativeai
)
pip show keyring >nul 2>&1
if errorlevel 1 (
    echo Installing keyring package...
    pip install keyring
)

echo.
echo Starting Gemini-Enhanced Flask server...
echo Keep this window OPEN while using the extension!
echo.
echo Features:
echo   ✓ AI-powered website navigation
echo   ✓ Intelligent assistance with Gemini
echo   ✓ Step-by-step guidance
echo.
echo Press Ctrl+C to stop the server
echo ============================================
echo.

python app_gemini.py

pause
