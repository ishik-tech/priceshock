#!/bin/bash

echo "========================================"
echo "  PriceShock - Starting Application"
echo "========================================"
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python is not installed"
    exit 1
fi

# Check Node.js
if ! command -v node &> /dev/null; then
    echo "ERROR: Node.js is not installed"
    exit 1
fi

echo "[1/4] Installing backend dependencies..."
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -q -r requirements.txt

echo ""
echo "[2/4] Initializing database with demo data..."
python init_db.py
cd ..

echo ""
echo "[3/4] Installing frontend dependencies..."
cd frontend
npm install
cd ..

echo ""
echo "[4/4] Starting services..."
echo ""
echo "Starting FastAPI backend on http://localhost:8000"
echo "Starting Next.js frontend on http://localhost:3000"
echo ""

# Start backend in background
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
cd ..

# Wait for backend
sleep 3

# Start frontend
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

echo ""
echo "========================================"
echo "  PriceShock is running..."
echo "========================================"
echo ""
echo "Backend API: http://localhost:8000"
echo "Frontend:    http://localhost:3000"
echo "API Docs:    http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all services"
echo ""

# Handle Ctrl+C
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null" EXIT

wait
