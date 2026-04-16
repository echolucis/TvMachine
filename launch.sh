#!/bin/bash

# ============================================================
# IPTV/EPG System - One-Click Launcher (Linux/Mac)
# ============================================================
# This script will:
# 1. Check for Python and Node.js installations
# 2. Install Python dependencies if needed
# 3. Install Node.js dependencies if needed
# 4. Run the data pipeline to fetch/process M3U and XMLTV
# 5. Start the FastAPI backend server
# 6. Start the Vite frontend dev server
# ============================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$SCRIPT_DIR/backend"
FRONTEND_DIR="$SCRIPT_DIR/frontend"

echo ""
echo "========================================"
echo "  IPTV/EPG System - One-Click Launcher"
echo "========================================"
echo ""

# --- Check Python ---
echo "[1/6] Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python3 not found! Please install Python 3.8+"
    exit 1
fi
python3 --version
echo "Python OK."

# --- Check Node.js ---
echo ""
echo "[2/6] Checking Node.js installation..."
if ! command -v node &> /dev/null; then
    echo "ERROR: Node.js not found! Please install Node.js 16+"
    exit 1
fi
node --version
echo "Node.js OK."

# --- Install Python Dependencies ---
echo ""
echo "[3/6] Installing Python dependencies..."
cd "$BACKEND_DIR"
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi
echo "Activating virtual environment..."
source venv/bin/activate
echo "Installing requirements from requirements.txt..."
pip install -r requirements.txt
echo "Python dependencies ready."

# --- Install Node.js Dependencies ---
echo ""
echo "[4/6] Installing Node.js dependencies..."
cd "$FRONTEND_DIR"
if [ ! -d "node_modules" ]; then
    echo "Running npm install..."
    npm install
fi
echo "Node.js dependencies ready."

# --- Run Data Pipeline ---
echo ""
echo "[5/6] Running data pipeline (fetching M3U/XMLTV and building guide)..."
cd "$BACKEND_DIR"
source venv/bin/activate
echo "This may take 1-2 minutes depending on your internet connection..."
python run_pipeline.py || echo "WARNING: Pipeline encountered issues, but continuing..."
echo "Data pipeline complete."

# --- Start Servers ---
echo ""
echo "[6/6] Starting servers..."
echo ""
echo "========================================"
echo "  BACKEND API: http://localhost:8000"
echo "  FRONTEND UI: http://localhost:5173"
echo "========================================"
echo ""
echo "Press Ctrl+C in each terminal to stop servers."
echo ""
echo "Starting backend in background..."
cd "$BACKEND_DIR"
source venv/bin/activate
python main.py --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
echo "Backend started (PID: $BACKEND_PID)"

sleep 3

echo "Starting frontend in background..."
cd "$FRONTEND_DIR"
npm run dev &
FRONTEND_PID=$!
echo "Frontend started (PID: $FRONTEND_PID)"

echo ""
echo "Both servers are running!"
echo ""
echo "API Documentation: http://localhost:8000/docs"
echo "Web Interface: http://localhost:5173"
echo ""
echo "Press Ctrl+C to stop all servers..."
wait
