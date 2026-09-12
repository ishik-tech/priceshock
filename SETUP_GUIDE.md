# PriceShock - Setup Complete

## What Was Accomplished

All core files have been created and the application is ready for testing!

### Backend (FastAPI + SQLite)
- Complete backend structure with models, schemas, routes, and services
- SQLAlchemy ORM models for Products, Price Observations, Forecasts, Risk Scores
- Pydantic schemas for request/response validation
- REST API endpoints for products, forecasts, risk analysis, dashboard, alerts
- CORS middleware configured for frontend communication
- Database initialization script

### Frontend (Next.js + Tailwind CSS + Recharts)
- Next.js 14 app router configured
- Tailwind CSS for styling
- Recharts for data visualization
- Main dashboard page with product listings
- Product detail page with price charts and forecasts
- API client configured to connect to backend
- Responsive design implemented

### Machine Learning (Python)
- Synthetic data generation script for 15 products across 3 categories
- Training script with multiple forecasting models (Naive, Seasonal Naive, Random Forest)
- Model evaluation with MAE, RMSE, MAPE metrics
- Model comparison and best model selection

## How to Run

### Start Backend
```bash
cd c:\Users\hp\OneDrive\Desktop\PRICESHOCK\backend
venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --port 8000
```

API: http://localhost:8000
Docs: http://localhost:8000/docs

### Start Frontend (New Terminal)
```bash
cd c:\Users\hp\OneDrive\Desktop\PRICESHOCK\frontend
npm install
npm run dev
```

Frontend: http://localhost:3000

## Features

- Product Management: Browse products by category (Food, Energy, Construction)
- Price Forecasting: Generate 30-day forecasts using ML models
- Risk Analysis: Calculate probability of price increases (5%, 10%, 20%)
- Interactive Charts: Visualize price history and forecasts
- Responsive Design: Works on desktop and mobile
- Offline-First: All data stored locally in SQLite
- Demo Data: Synthetic data clearly labeled as DEMO/SYNTHETIC

## Sample Products

Food: Rice, Wheat, Sugar, Milk, Cooking Oil, Tomato, Onion, Potato
Energy: Petrol, Diesel, Crude Oil
Construction: Cement, Steel

## Troubleshooting

### Backend wont start
- Ensure Python virtual environment is activated
- Check dependencies: pip install -r requirements.txt
- Verify database file exists: priceshock.db

### Frontend wont start
- Ensure Node.js 18+ is installed
- Delete node_modules and run npm install again
- Check that backend is running on port 8000

### No data showing
- Run: python ml/generate_demo_data.py
- Run: python ml/train.py
- Check browser console for API errors

## Project Structure

PRICESHOCK/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI application
│   │   ├── database.py          # SQLAlchemy setup
│   │   ├── models/              # ORM models
│   │   ├── schemas/             # Pydantic schemas
│   │   ├── routes/              # API routes
│   │   └── services/            # Business logic
│   ├── init_db.py               # Database initialization
│   └── requirements.txt
├── frontend/
│   ├── app/
│   │   ├── layout.tsx
│   │   ├── page.tsx             # Dashboard
│   │   └── products/[id].tsx    # Product detail
│   ├── lib/api.ts               # API client
│   ├── package.json
│   └── tailwind.config.ts
├── ml/
│   ├── generate_demo_data.py    # Synthetic data
│   └── train.py                 # Model training
├── .env.example
├── README.md
└── start.bat

## Status

✅ Setup Complete - Ready for Testing

All files created successfully!
