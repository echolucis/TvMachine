@echo off
setlocal enabledelayedexpansion

:: ============================================================
:: IPTV/EPG System - One-Click Launcher (Windows)
:: ============================================================
:: This script will:
:: 1. Check for Python and Node.js installations
:: 2. Install Python dependencies if needed
:: 3. Install Node.js dependencies if needed
:: 4. Run the data pipeline to fetch/process M3U and XMLTV
:: 5. Start the FastAPI backend server
:: 6. Start the Vite frontend dev server
:: ============================================================

echo.
echo ========================================
echo   IPTV/EPG System - One-Click Launcher
echo ========================================
echo.

:: --- Configuration ---
set "PYTHON_CMD=python"
set "NODE_CMD=node"
set "NPM_CMD=npm"
set "BACKEND_DIR=%~dp0backend"
set "FRONTEND_DIR=%~dp0frontend"

:: --- Check Python ---
echo [1/6] Checking Python installation...
%PYTHON_CMD% --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python not found! Please install Python 3.8+ from https://python.org
    echo Make sure to check "Add Python to PATH" during installation.
    pause
    exit /b 1
)
%PYTHON_CMD% --version
echo Python OK.

:: --- Check Node.js ---
echo.
echo [2/6] Checking Node.js installation...
%NODE_CMD% --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Node.js not found! Please install Node.js 16+ from https://nodejs.org
    pause
    exit /b 1
)
%NODE_CMD% --version
echo Node.js OK.

:: --- Install Python Dependencies ---
echo.
echo [3/6] Installing Python dependencies...
cd /d "%BACKEND_DIR%"
if not exist "venv" (
    echo Creating virtual environment...
    %PYTHON_CMD% -m venv venv
)
echo Activating virtual environment...
call venv\Scripts\activate.bat
echo Installing requirements from requirements.txt...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo WARNING: Some packages may have failed to install, continuing anyway...
)
echo Python dependencies ready.

:: --- Install Node.js Dependencies ---
echo.
echo [4/6] Installing Node.js dependencies...
cd /d "%FRONTEND_DIR%"
if not exist "node_modules" (
    echo Running npm install...
    call %NPM_CMD% install
    if %errorlevel% neq 0 (
        echo ERROR: npm install failed!
        pause
        exit /b 1
    )
)
echo Node.js dependencies ready.

:: --- Run Data Pipeline ---
echo.
echo [5/6] Running data pipeline (fetching M3U/XMLTV and building guide)...
cd /d "%BACKEND_DIR%"
call venv\Scripts\activate.bat
echo This may take 1-2 minutes depending on your internet connection...
%PYTHON_CMD% run_pipeline.py
if %errorlevel% neq 0 (
    echo WARNING: Pipeline encountered issues, but continuing to start servers...
    echo You may see empty data until the next successful run.
)
echo Data pipeline complete.

:: --- Start Backend Server ---
echo.
echo [6/6] Starting servers...
echo.
echo ========================================
echo   BACKEND API: http://localhost:8000
echo   FRONTEND UI: http://localhost:5173
echo ========================================
echo.
echo Press Ctrl+C to stop all servers.
echo.

:: Start backend in a new window
start "IPTV Backend API" cmd /k "cd /d %BACKEND_DIR% && call venv\Scripts\activate.bat && echo Starting FastAPI server... && python main.py --host 0.0.0.0 --port 8000"

:: Wait a moment for backend to initialize
timeout /t 3 /nobreak >nul

:: Start frontend in a new window
start "IPTV Frontend UI" cmd /k "cd /d %FRONTEND_DIR% && echo Starting Vite dev server... && npm run dev"

echo.
echo Both servers are starting in separate windows.
echo Check the new command windows for status.
echo.
echo API Documentation: http://localhost:8000/docs
echo Web Interface: http://localhost:5173
echo.
pause
