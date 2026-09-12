Write-Host "=== PriceShock Setup ===" -ForegroundColor Green

# Step 1: Create backend venv
Write-Host "`n[1/6] Creating backend virtual environment..." -ForegroundColor Yellow
cd backend
python -m venv venv
Write-Host "Virtual environment created"

# Step 2: Install backend dependencies
Write-Host "`n[2/6] Installing backend dependencies (this may take a few minutes)..." -ForegroundColor Yellow
.\venv\Scripts\pip.exe install -q fastapi==0.104.1 uvicorn==0.24.0 sqlalchemy==2.0.23 pydantic==2.5.0 pandas==2.1.3 numpy==1.26.2 scikit-learn==1.3.2 statsmodels==0.14.0 joblib==1.3.2 python-dotenv==1.0.0 aiofiles==23.2.1 requests==2.31.0
Write-Host "Backend dependencies installed"

# Step 3: Install frontend dependencies
Write-Host "`n[3/6] Installing frontend dependencies..." -ForegroundColor Yellow
cd ../frontend
npm install
Write-Host "Frontend dependencies installed"

# Step 4: Initialize database
Write-Host "`n[4/6] Initializing database..." -ForegroundColor Yellow
cd ../backend
python init_db.py
Write-Host "Database initialized"

# Step 5: Generate demo data and train models
Write-Host "`n[5/6] Generating demo data and training models..." -ForegroundColor Yellow
cd ../ml
python generate_demo_data.py
python train.py
Write-Host "Models trained"

# Step 6: Done
Write-Host "`n[6/6] Setup complete!" -ForegroundColor Green
Write-Host "`nTo start the application:" -ForegroundColor Cyan
Write-Host "  Backend: cd backend && venv\Scripts\activate && uvicorn app.main:app --reload --port 8000"
Write-Host "  Frontend: cd frontend && npm run dev"
Write-Host "`nURLs:" -ForegroundColor Cyan
Write-Host "  Frontend: http://localhost:3000"
Write-Host "  Backend: http://localhost:8000"
Write-Host "  API Docs: http://localhost:8000/docs"
