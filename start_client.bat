@echo off
setlocal

:: Default values
set DEVICE_ID=jetson-001
set SERVER_URL=http://localhost:8000
set API_KEY=your_api_key_here
set CAMERA_INDEX=0

:: Parse command line arguments
:parse
if "%~1"=="" goto :start
if "%~1"=="--device-id" (
    set DEVICE_ID=%~2
    shift
    shift
    goto :parse
)
if "%~1"=="--server-url" (
    set SERVER_URL=%~2
    shift
    shift
    goto :parse
)
if "%~1"=="--api-key" (
    set API_KEY=%~2
    shift
    shift
    goto :parse
)
if "%~1"=="--camera-index" (
    set CAMERA_INDEX=%~2
    shift
    shift
    goto :parse
)
shift
goto :parse

:start
echo Starting Edge Client...
echo Device ID: %DEVICE_ID%
echo Server URL: %SERVER_URL%
echo Camera Index: %CAMERA_INDEX%

:: Activate virtual environment
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
) else (
    echo Virtual environment not found. Please run start_server.bat first.
    pause
    exit /b 1
)

:: Install client dependencies
pip install opencv-python requests

:: Start client
cd edge
python client.py --device-id "%DEVICE_ID%" --server-url "%SERVER_URL%" --api-key "%API_KEY%" --camera-index %CAMERA_INDEX%

pause
