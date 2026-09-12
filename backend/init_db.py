#!/usr/bin/env python3
"""
Initialize the database with demo data
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
import json

from app.database import Base, init_db
from app.models import Product, PriceObservation, DataSource


def create_demo_data():
    """Create demo products and price data"""
    
    # Create engine
    engine = create_engine("sqlite:///./priceshock.db", connect_args={"check_same_thread": False})
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    print("Creating tables...")
    Base.metadata.create_all(bind=engine)
    
    # Check if data already exists
    existing = db.query(Product).first()
    if existing:
        print("Database already initialized. Skipping.")
        return
    
    print("Creating products...")
    products_data = [
        ("Rice", "Food", "kg", "National", "Basmati rice (medium grain)"),
        ("Wheat", "Food", "kg", "National", "Wheat flour (atta)"),
        ("Sugar", "Food", "kg", "National", "Refined sugar"),
        ("Milk", "Food", "litre", "National", "Cow milk (1 litre)"),
        ("Cooking Oil", "Food", "litre", "National", "Sunflower oil (1 litre)"),
        ("Tomato", "Food", "kg", "National", "Fresh tomatoes (highly seasonal)"),
        ("Onion", "Food", "kg", "National", "Onions (very volatile)"),
        ("Potato", "Food", "kg", "National", "Potatoes"),
        ("Petrol", "Energy", "litre", "National", "Petrol (correlated with crude oil)"),
        ("Diesel", "Energy", "litre", "National", "Diesel fuel"),
        ("Crude Oil", "Energy", "barrel", "International", "Crude oil (international benchmark)"),
        ("Cement", "Construction", "bag", "National", "OPC cement (50kg bag)"),
        ("Steel", "Construction", "kg", "National", "Steel rebar"),
    ]
    
    products = []
    for i, (name, category, unit, region, desc) in enumerate(products_data, 1):
        product = Product(
            id=i,
            name=name,
            category=category,
            unit=unit,
            region=region,
            description=desc,
        )
        db.add(product)
        products.append(product)
    
    db.commit()
    print(f"Created {len(products)} products")
    
    print("Creating price observations...")
    end_date = datetime.now()
    start_date = end_date - timedelta(days=3*365)
    
    import numpy as np
    
    total_observations = 0
    for product in products:
        # Generate realistic price data
        base_prices = {
            "Rice": 45.0, "Wheat": 30.0, "Sugar": 42.0, "Milk": 60.0,
            "Cooking Oil": 120.0, "Tomato": 35.0, "Onion": 28.0, "Potato": 22.0,
            "Petrol": 100.0, "Diesel": 90.0, "Crude Oil": 75.0, "Cement": 400.0, "Steel": 65.0
        }
        
        volatilities = {
            "Rice": 0.02, "Wheat": 0.025, "Sugar": 0.03, "Milk": 0.015,
            "Cooking Oil": 0.04, "Tomato": 0.15, "Onion": 0.2, "Potato": 0.12,
            "Petrol": 0.025, "Diesel": 0.03, "Crude Oil": 0.05, "Cement": 0.02, "Steel": 0.035
        }
        
        base_price = base_prices.get(product.name, 50.0)
        volatility = volatilities.get(product.name, 0.03)
        current_date = start_date
        current_price = base_price
        
        while current_date <= end_date:
            # Random walk
            change = np.random.normal(0, volatility * current_price)
            
            # Seasonal component
            day_of_year = current_date.timetuple().tm_yday
            seasonal = 0.05 * base_price * np.sin(2 * np.pi * day_of_year / 365)
            
            # Occasional shock
            if np.random.random() < 0.02:
                change += np.random.normal(0, volatility * base_price * 2)
            
            current_price = max(base_price * 0.5, current_price + change + seasonal * 0.01)
            
            observation = PriceObservation(
                product_id=product.id,
                date=current_date,
                price=round(current_price, 2),
                currency="INR",
                unit=product.unit,
                region=product.region,
                source="Demo / Synthetic Data",
                is_synthetic=True,
            )
            db.add(observation)
            total_observations += 1
            current_date += timedelta(days=1)
    
    db.commit()
    print(f"Created {total_observations} price observations")
    
    # Create data source
    data_source = DataSource(
        name="Demo / Synthetic Data",
        source_type="synthetic",
        description="Synthetic price data generated for demonstration purposes",
        last_updated=datetime.now(),
        is_active=1,
        metadata_json=json.dumps({
            "total_products": len(products),
            "total_observations": total_observations,
            "date_range": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat(),
            },
            "note": "This is synthetic data for demonstration purposes."
        }),
    )
    db.add(data_source)
    db.commit()
    
    print("Database initialized successfully!")
    print(f"Total products: {len(products)}")
    print(f"Total observations: {total_observations}")
    print(f"Date range: {start_date.date()} to {end_date.date()}")


if __name__ == "__main__":
    print("=" * 60)
    print("PriceShock - Database Initialization")
    print("=" * 60)
    print()
    create_demo_data()
    print()
    print("=" * 60)