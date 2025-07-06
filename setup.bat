@echo off
REM Twitter Hoax Detector - Quick Setup Script for Windows

echo 🚀 Twitter Hoax Detector - Quick Setup for Windows
echo ===================================================

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found! Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

echo ✅ Python found

REM Check Python version
for /f "tokens=2" %%i in ('python --version') do set PYTHON_VERSION=%%i
echo ✅ Python version: %PYTHON_VERSION%

REM Create virtual environment
echo 📦 Creating virtual environment...
if not exist "venv" (
    python -m venv venv
    echo ✅ Virtual environment created
) else (
    echo ℹ️ Virtual environment already exists
)

REM Activate virtual environment
echo 🔄 Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo 📦 Upgrading pip...
python -m pip install --upgrade pip

REM Install minimal requirements first
echo 📦 Installing minimal requirements...
if exist "requirements-minimal.txt" (
    pip install -r requirements-minimal.txt
    if errorlevel 1 (
        echo ❌ Failed to install minimal requirements
        pause
        exit /b 1
    )
    echo ✅ Minimal requirements installed
)

REM Try to install full requirements
echo 📦 Installing full requirements...
if exist "requirements.txt" (
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ⚠️ Some full requirements failed - continuing with minimal setup
    ) else (
        echo ✅ Full requirements installed
    )
)

REM Create directories
echo 📁 Creating directories...
if not exist "reports" mkdir reports
if not exist "visualizations" mkdir visualizations
if not exist "static" mkdir static
if not exist "templates" mkdir templates
if not exist "logs" mkdir logs
if not exist "app" mkdir app
if not exist "app\services" mkdir app\services
echo ✅ Directories created

REM Create config files
echo ⚙️ Creating configuration files...
if not exist ".env" (
    echo # Twitter Hoax Detector Configuration > .env
    echo DEBUG=true >> .env
    echo OPENAI_API_KEY=your-openai-api-key-here >> .env
    echo TELEGRAM_BOT_TOKEN=your-telegram-bot-token-here >> .env
    echo USE_REAL_TWITTER_API=false >> .env
    echo USE_REAL_BRAVE_API=false >> .env
    echo ✅ .env file created
) else (
    echo ℹ️ .env file already exists
)

REM Create __init__.py files
echo. > app\__init__.py
echo. > app\services\__init__.py

REM Test installation
echo 🧪 Testing installation...
python -c "
import sys
try:
    import fastapi
    import uvicorn
    import sqlalchemy
    print('✅ Core modules imported successfully')
    sys.exit(0)
except ImportError as e:
    print(f'❌ Import error: {e}')
    sys.exit(1)
"

if errorlevel 1 (
    echo ❌ Installation test failed
    echo ⚠️ Setup completed with warnings - check installation
) else (
    echo ✅ Installation test passed
    echo 🎉 Setup completed successfully!
)

echo.
echo ===================
echo 📋 Next steps:
echo 1. Edit .env file with your API keys:
echo    notepad .env
echo.
echo 2. Activate virtual environment (in new terminal):
echo    venv\Scripts\activate.bat
echo.
echo 3. Run the application:
echo    python run.py both
echo.
echo 4. Access the dashboard:
echo    http://localhost:8000
echo.
echo 📚 Documentation: README.md
echo 🐛 Issues: Check the logs\ directory
echo.

pause 