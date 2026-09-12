"Generate realistic synthetic price data for demonstration purposes.
All data is labeled as DEMO / SYNTHETIC.
"

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import json


PRODUCTS = {
    "rice": {"name": "Rice", "category": "Food", "unit": "kg", "base_price": 45.0, "volatility": 0.02, "seasonality": 0.05, "trend": 0.001, "description": "Basmati rice (medium grain)"},
    "wheat": {"name": "Wheat", "category": "Food", "unit": "kg", "base_price": 30.0, "volatility": 0.025, "seasonality": 0.08, "trend": 0.0005, "description": "Wheat flour (atta)"},
    "sugar": {"name": "Sugar", "category": "Food", "unit": "kg", "base_price": 42.0, "volatility": 0.03, "seasonality": 0.1, "trend": 0.002, "description": "Refined sugar"},
    "milk": {"name": "Milk", "category": "Food", "unit": "litre", "base_price": 60.0, "volatility": 0.015, "seasonality": 0.03, "trend": 0.003, "description": "Cow milk (1 litre)"},
    "cooking_oil": {"name": "Cooking Oil", "category": "Food", "unit": "litre", "base_price": 120.0, "volatility": 0.04, "seasonality": 0.06, "trend": 0.002, "description": "Sunflower oil (1 litre)"},
    "tomato": {"name": "Tomato", "category": "Food", "unit": "kg", "base_price": 35.0, "volatility": 0.15, "seasonality": 0.3, "trend": 0.001, "description": "Fresh tomatoes (highly seasonal)"},
    "onion": {"name": "Onion", "category": "Food", "unit": "kg", "base_price": 28.0, "volatility": 0.2, "seasonality": 0.35, "trend": 0.001, "description": "Onions (very volatile)"},
    "potato": {"name": "Potato", "category": "Food", "unit": "kg", "base_price": 22.0, "volatility": 0.12, "seasonality": 0.25, "trend": 0.0005, "description": "Potatoes"},
    "petrol": {"name": "Petrol", "category": "Energy", "unit": "litre", "base_price": 100.0, "volatility": 0.025, "seasonality": 0.04, "trend": 0.003, "description": "Petrol (correlated with crude oil)"},
    "diesel": {"name": "Diesel", "category": "Energy", "unit": "litre", "base_price": 90.0, "volatility": 0.03, "seasonality": 0.04, "trend": 0.003, "description": "Diesel fuel"},
    "crude_oil": {"name": "Crude Oil", "category": "Energy", "unit": "barrel", "base_price": 75.0, "volatility": 0.05, "seasonality": 0.06, "trend": 0.002, "description": "Crude oil (international benchmark)"},
    "cement": {"name": "Cement", "category": "Construction", "unit": "bag", "base_price": 400.0, "volatility": 0.02, "seasonality": 0.05, "trend": 0.004, "description": "OPC cement (50kg bag)"},
    "steel": {"name": "Steel", "category": "Construction", "unit": "kg", "base_price": 65.0, "volatility": 0.035, "seasonality": 0.05, "trend": 0.003, "description": "Steel rebar"},
}


def generate_price_series(base_price, days, volatility, seasonality, trend, start_date, seed=42):
    np.random.seed(seed)
    dates = [start_date + timedelta(days=i) for i in range(days)]
    prices = []
    current_price = base_price

    for i, date in enumerate(dates):
        trend_component = trend * i
        day_of_year = date.timetuple().tm_yday
        seasonal_component = seasonality * base_price * np.sin(2 * np.pi * day_of_year / 365)
        shock = np.random.normal(0, volatility * current_price)

        if np.random.random() < 0.05:
            shock += np.random.normal(0, volatility * base_price * 3)

        current_price = current_price + trend_component + seasonal_component + shock
        current_price = max(base_price * 0.5, current_price)
        prices.append(current_price)

    return pd.DataFrame({"date": dates, "price": prices})


def generate_all_data(output_dir="ml/data/raw"):
    os.makedirs(output_dir, exist_ok=True)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=3*365)
    days = (end_date - start_date).days

    all_observations = []
    products_metadata = []

    for product_id, (key, product_info) in enumerate(PRODUCTS.items(), start=1):
        print(f"Generating data for {product_info['name']}...")
        df = generate_price_series(
            base_price=product_info["base_price"],
            days=days,
            volatility=product_info["volatility"],
            seasonality=product_info["seasonality"],
            trend=product_info["trend"],
            start_date=start_date,
            seed=42 + product_id
        )
        df["product_id"] = product_id
        df["product_name"] = product_info["name"]
        df["category"] = product_info["category"]
        df["unit"] = product_info["unit"]
        df["source"] = "Demo / Synthetic Data"
        df["is_synthetic"] = True
        all_observations.append(df)
        products_metadata.append({"id": product_id, "key": key, **product_info})

    combined_df = pd.concat(all_observations, ignore_index=True)
    output_file = os.path.join(output_dir, "price_observations.csv")
    combined_df.to_csv(output_file, index=False)
    print(f"Saved {len(combined_df)} observations to {output_file}")

    metadata_file = os.path.join(output_dir, "products.json")
    with open(metadata_file, "w") as f:
        json.dump(products_metadata, f, indent=2, default=str)
    print(f"Saved {len(products_metadata)} products to {metadata_file}")

    return combined_df, products_metadata


if __name__ == "__main__":
    print("=" * 60)
    print("PriceShock - Demo Data Generation")
    print("=" * 60)
    df, products = generate_all_data()
    print()
    print(f"Products: {len(products)}")
    print(f"Total observations: {len(df)}")
    print(f"Date range: {df['date'].min()} to {df['date'].max()}")
    print("=" * 60)
