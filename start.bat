@echo off
echo ========================================
echo   PriceShock - Starting Application
echo ========================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Check Node.js
node --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Node.js is not installed or not in PATH
    pause
    exit /b 1
)

echo [1/4] Installing backend dependencies...
cd backend
python -m venv venv
call venv\Scripts\activate.bat
pip install -q -r requirements.txt

echo.
echo [2/4] Initializing database with demo data...
python init_db.py
cd ..

echo.
echo [3/4] Installing frontend dependencies...
cd frontend
call npm install
cd ..

echo.
echo [4/4] Starting services...
echo.
echo Starting FastAPI backend on http://localhost:8000
echo Starting Next.js frontend on http://localhost:3000
echo.

REM Start backend in new window
start "PriceShock Backend" cmd /c "cd backend && venv\Scripts\activate.bat && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"

REM Wait a moment for backend to start
timeout /t 5 /nobreak >nul

REM Start frontend in new window
start "PriceShock Frontend" cmd /c "cd frontend && npm run dev"

echo.
echo ========================================
echo   PriceShock is starting...
echo ========================================
echo.
echo Backend API: http://localhost:8000
echo Frontend:    http://localhost:3000
echo API Docs:    http://localhost:8000/docs
echo.
echo Press Ctrl+C to stop all services
echo.

pause
