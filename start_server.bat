@echo off
echo Starting Edge Anomaly Detection Server...

:: Check if virtual environment exists
if not exist "venv\" (
    echo Creating virtual environment...
    python -m venv venv
)

:: Activate virtual environment
call venv\Scripts\activate.bat

:: Install dependencies
echo Installing dependencies...
pip install -r requirements.txt

:: Create .env file if it doesn't exist
if not exist ".env" (
    echo Creating .env file from template...
    copy .env.example .env
    echo Please edit .env file with your configuration before running the server
    pause
)

:: Create data directories
if not exist "data\" mkdir data
if not exist "logs\" mkdir logs

:: Start server
echo Starting FastAPI server...
cd server
python main.py

pause
