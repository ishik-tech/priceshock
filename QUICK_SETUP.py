#!/usr/bin/env python3
"""
Quick setup script for PriceShock
"""
import subprocess
import sys
import os

def run(cmd, desc):
    print(f"\n{desc}...")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"ERROR: {result.stderr}")
        sys.exit(1)
    print(f"✓ {desc} complete")

os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Install backend
run("cd backend && python -m venv venv && venv\\Scripts\\pip.exe install -q fastapi uvicorn sqlalchemy pydantic pandas numpy scikit-learn statsmodels joblib python-dotenv aiofiles requests", "Installing backend dependencies")

# Install frontend  
run("cd frontend && npm install", "Installing frontend dependencies")

# Init database
run("cd backend && python init_db.py", "Initializing database")

# Generate data and train
run("cd ml && python generate_demo_data.py && python train.py", "Generating data and training models")

print("\n" + "="*60)
print("SETUP COMPLETE!")
print("="*60)
print("\nTo run:")
print("  Backend: cd backend && venv\\Scripts\\activate && uvicorn app.main:app --reload --port 8000")
print("  Frontend: cd frontend && npm run dev")
print("\nURLs:")
print("  Frontend: http://localhost:3000")
print("  Backend: http://localhost:8000")
print("  API Docs: http://localhost:8000/docs")
