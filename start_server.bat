@echo off
echo ============================================
echo Starting TN Government Chatbot Server
echo ============================================
echo.

cd /d %~dp0

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo Starting Flask server...
echo Keep this window OPEN while using the extension!
echo.
echo Press Ctrl+C to stop the server
echo ============================================
echo.

python app.py

pause
