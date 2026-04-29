@echo off
echo.
echo ===============================================
echo   Advanced NL-to-SQL System - Enhanced Setup
echo ===============================================
echo.

:: Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

echo ✅ Python detected
echo.

:: Install dependencies
echo 📦 Installing enhanced dependencies...
echo.
echo Installing core packages...
pip install pandas numpy matplotlib seaborn python-dotenv

echo.
echo Installing AI/ML packages...
pip install google-generativeai sentence-transformers faiss-cpu scikit-learn

echo.
echo Installing web interface packages...
pip install flask flask-cors

echo.
echo Installing visualization packages...
pip install plotly kaleido

echo.
echo Installing export functionality...
pip install openpyxl xlsxwriter

if %errorlevel% neq 0 (
    echo.
    echo ❌ Some dependencies failed to install
    echo Try installing manually or check your internet connection
    pause
    exit /b 1
)

echo.
echo ✅ All dependencies installed successfully!
echo.

:: Check if .env needs setup
if not exist .env (
    echo ⚠️  Please set up your .env file with API keys
    echo   1. Edit .env file
    echo   2. Add your GEMINI_API_KEY from https://makersuite.google.com/app/apikey
    echo.
) else (
    echo ✅ Environment file found
)

:: Create directories
if not exist data mkdir data
if not exist visualizations mkdir visualizations
if not exist logs mkdir logs
if not exist templates mkdir templates

echo ✅ Enhanced project structure ready!
echo.
echo 🚀 Getting Started:
echo   1. Edit .env file and add your GEMINI_API_KEY
echo   2. Run: python main.py
echo   3. Choose interface mode:
echo      - Option 1: Command Line Interface
echo      - Option 2: Web Interface (http://localhost:5000)
echo      - Option 3: Quick Demo
echo.
echo 📊 Features Available:
echo   ✅ Natural Language to SQL conversion
echo   ✅ Interactive web interface
echo   ✅ Dynamic visualizations (Plotly + Matplotlib)
echo   ✅ Export to CSV, Excel, JSON
echo   ✅ Enhanced database with sample data
echo   ✅ AI-powered query similarity matching
echo.
echo 📖 See README.md for detailed instructions
echo.
pause