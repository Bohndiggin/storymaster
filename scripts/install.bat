@echo off
REM Storymaster Installation Script for Windows

echo 🏰 Installing Storymaster...
echo ==============================

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed. Please install Python 3.8+ and try again.
    pause
    exit /b 1
)

REM Run the Python installer
python install.py

echo.
echo 🎉 Installation complete!
echo.
echo To run Storymaster:
echo   .venv\Scripts\activate
echo   python storymaster\main.py
pause