import os
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
from sqlalchemy.orm import Session

from app.models.forecast_prediction import ForecastPrediction
from app.models.forecast_run import ForecastRun
from app.models.model_metrics import ModelMetrics
from app.models.price_observation import PriceObservation


class ForecastingService:
    """Service for generating price forecasts using multiple models"""

    def __init__(self, db: Session, models_dir: str = "./ml/models"):
        self.db = db
        self.models_dir = models_dir
        os.makedirs(models_dir, exist_ok=True)

    def get_price_history(self, product_id: int, min_days: int = 90) -> pd.DataFrame:
        """Get price history for a product"""
        observations = (
            self.db.query(PriceObservation)
            .filter(PriceObservation.product_id == product_id)
            .order_by(PriceObservation.date)
            .all()
        )

        if len(observations) < min_days:
            return pd.DataFrame()

        data = []
        for obs in observations:
            data.append({
                "date": obs.date,
                "price": obs.price,
                "product_id": obs.product_id
            })

        df = pd.DataFrame(data)
        df["date"] = pd.to_datetime(df["date"])
        df = df.set_index("date").sort_index()
        df = df.asfreq("D").ffill()
        df["product_id"] = df["product_id"].astype(int)

        return df

    def select_best_model(self, product_id: int) -> str:
        """Select the best model based on historical performance"""
        best_model = self.db.query(ModelMetrics).filter(
            ModelMetrics.product_id == product_id
        ).order_by(ModelMetrics.mae.asc()).first()

        if best_model:
            return best_model.model_name

        return "seasonal_naive"

    def generate_forecast(
        self,
        product_id: int,
        horizon_days: int = 30,
        model_name: str | None = None
    ) -> dict | None:
        """Generate forecast for a product"""

        df = self.get_price_history(product_id)

        if df.empty or len(df) < 30:
            return None

        if not model_name:
            model_name = self.select_best_model(product_id)

        current_price = float(df["price"].iloc[-1])
        last_date = df.index[-1]

        if model_name == "naive":
            predictions = self._naive_forecast(df, horizon_days, last_date)
        elif model_name == "seasonal_naive":
            predictions = self._seasonal_naive_forecast(df, horizon_days, last_date)
        elif model_name == "arima":
            predictions = self._arima_forecast(df, horizon_days, last_date)
        elif model_name == "random_forest":
            predictions = self._random_forest_forecast(df, horizon_days, last_date)
        else:
            predictions = self._naive_forecast(df, horizon_days, last_date)

        if not predictions:
            return None

        final_price = predictions[-1]["predicted_price"]
        expected_change_pct = ((final_price - current_price) / current_price) * 100

        # Save forecast run
        forecast_run = ForecastRun(
            product_id=product_id,
            model_name=model_name,
            horizon_days=horizon_days,
        )
        self.db.add(forecast_run)
        self.db.flush()

        # Save predictions
        for pred in predictions:
            forecast_pred = ForecastPrediction(
                forecast_run_id=forecast_run.id,
                forecast_date=pred["forecast_date"],
                predicted_price=pred["predicted_price"],
                lower_bound=pred.get("lower_bound"),
                upper_bound=pred.get("upper_bound"),
                horizon_days=pred["horizon_days"],
            )
            self.db.add(forecast_pred)

        self.db.commit()

        return {
            "product_id": product_id,
            "model_used": model_name,
            "horizon_days": horizon_days,
            "current_price": current_price,
            "predictions": predictions,
            "expected_change_pct": expected_change_pct,
        }

    def _naive_forecast(self, df: pd.DataFrame, horizon: int, last_date: datetime) -> list[dict]:
        """Simple naive forecast"""
        last_price = float(df["price"].iloc[-1])
        recent_std = float(df["price"].tail(30).std()) if len(df) >= 30 else float(df["price"].std())
        predictions = []

        for i in range(1, horizon + 1):
            forecast_date = last_date + timedelta(days=i)
            variation = np.random.normal(0, recent_std * 0.1)

            predictions.append({
                "forecast_date": forecast_date,
                "predicted_price": max(0, last_price + variation),
                "lower_bound": max(0, last_price - recent_std * 1.5),
                "upper_bound": last_price + recent_std * 1.5,
                "horizon_days": i,
            })

        return predictions

    def _seasonal_naive_forecast(self, df: pd.DataFrame, horizon: int, last_date: datetime) -> list[dict]:
        """Seasonal naive forecast"""
        predictions = []
        recent_std = float(df["price"].tail(30).std()) if len(df) >= 30 else float(df["price"].std())

        for i in range(1, horizon + 1):
            forecast_date = last_date + timedelta(days=i)
            try:
                last_year_date = forecast_date - timedelta(days=365)
                if last_year_date in df.index:
                    seasonal_price = float(df.loc[last_year_date, "price"])
                else:
                    seasonal_price = float(df["price"].mean())
            except (KeyError, ValueError, TypeError):
                seasonal_price = float(df["price"].mean())

            predictions.append({
                "forecast_date": forecast_date,
                "predicted_price": max(0, seasonal_price),
                "lower_bound": max(0, seasonal_price - recent_std * 1.5),
                "upper_bound": seasonal_price + recent_std * 1.5,
                "horizon_days": i,
            })

        return predictions

    def _arima_forecast(self, df: pd.DataFrame, horizon: int, last_date: datetime) -> list[dict]:
        """ARIMA forecast"""
        try:
            from statsmodels.tsa.arima.model import ARIMA

            model = ARIMA(df["price"], order=(2, 1, 2))
            fitted = model.fit()

            forecast_result = fitted.get_forecast(steps=horizon)
            forecast_mean = forecast_result.predicted_mean
            forecast_ci = forecast_result.conf_int(alpha=0.05)

            predictions = []
            for i in range(horizon):
                forecast_date = last_date + timedelta(days=i + 1)
                predictions.append({
                    "forecast_date": forecast_date,
                    "predicted_price": max(0, float(forecast_mean.iloc[i])),
                    "lower_bound": max(0, float(forecast_ci.iloc[i, 0])),
                    "upper_bound": float(forecast_ci.iloc[i, 1]),
                    "horizon_days": i + 1,
                })

            return predictions
        except Exception as e:
            print(f"ARIMA failed: {e}")
            return self._seasonal_naive_forecast(df, horizon, last_date)

    def _random_forest_forecast(self, df: pd.DataFrame, horizon: int, last_date: datetime) -> list[dict]:
        """Random Forest forecast"""
        try:
            from sklearn.ensemble import RandomForestRegressor

            # Create features
            df_features = df.copy()
            df_features["day_of_week"] = df_features.index.dayofweek
            df_features["month"] = df_features.index.month
            df_features["day_of_year"] = df_features.index.dayofyear
            df_features["price_lag1"] = df_features["price"].shift(1)
            df_features["price_lag7"] = df_features["price"].shift(7)
            df_features["price_lag30"] = df_features["price"].shift(30)
            df_features["rolling_mean_7"] = df_features["price"].rolling(window=7).mean()
            df_features["rolling_std_7"] = df_features["price"].rolling(window=7).std()
            df_features = df_features.dropna()

            if len(df_features) < 30:
                return self._seasonal_naive_forecast(df, horizon, last_date)

            feature_cols = [
                "day_of_week", "month", "day_of_year",
                "price_lag1", "price_lag7", "price_lag30",
                "rolling_mean_7", "rolling_std_7",
            ]
            X = df_features[feature_cols]
            y = df_features["price"]

            # Train model
            model = RandomForestRegressor(n_estimators=100, random_state=42)
            model.fit(X, y)

            # Generate forecasts
            predictions = []
            last_row = df_features.iloc[-1].copy()

            for i in range(1, horizon + 1):
                forecast_date = last_date + timedelta(days=i)

                # Update features
                last_row["day_of_week"] = forecast_date.weekday()
                last_row["month"] = forecast_date.month
                last_row["day_of_year"] = forecast_date.timetuple().tm_yday

                pred_price = float(model.predict([last_row[feature_cols]])[0])
                pred_price = max(0, pred_price)

                recent_std = float(df["price"].tail(30).std())

                predictions.append({
                    "forecast_date": forecast_date,
                    "predicted_price": pred_price,
                    "lower_bound": max(0, pred_price - recent_std * 1.5),
                    "upper_bound": pred_price + recent_std * 1.5,
                    "horizon_days": i,
                })

            return predictions
        except Exception as e:
            print(f"Random Forest failed: {e}")
            return self._seasonal_naive_forecast(df, horizon, last_date)

    def evaluate_model(self, df: pd.DataFrame, model_name: str) -> dict:
        """Evaluate model performance on test data"""
        if len(df) < 90:
            return {"error": "Insufficient data"}

        train_size = int(len(df) * 0.7)
        train = df.iloc[:train_size]
        test = df.iloc[train_size:]

        if len(test) < 7:
            return {"error": "Insufficient test data"}

        prediction_list: list[float] = []
        actual_list: list[float] = []

        for i in range(len(test) - 1):
            train_window = pd.concat([train, test.iloc[:i+1]])

            if model_name == "seasonal_naive":
                try:
                    last_year = test.index[i] - timedelta(days=365)
                    if last_year in df.index:
                        pred = float(df.loc[last_year, "price"])
                    else:
                        pred = float(train_window["price"].mean())
                except (KeyError, ValueError, TypeError):
                    pred = float(train_window["price"].mean())
            else:
                pred = float(train_window["price"].iloc[-1])

            prediction_list.append(pred)
            actual_list.append(float(test["price"].iloc[i+1]))

        predictions_arr = np.array(prediction_list)
        actuals_arr = np.array(actual_list)

        errors = np.abs(predictions_arr - actuals_arr)
        mae = float(np.mean(errors))
        rmse = float(np.sqrt(np.mean(errors ** 2)))
        mape = (
            float(np.mean(np.abs((actuals_arr - predictions_arr) / actuals_arr)) * 100)
            if np.all(actuals_arr != 0)
            else None
        )

        return {
            "model_name": model_name,
            "mae": mae,
            "rmse": rmse,
            "mape": mape,
            "test_samples": len(prediction_list),
        }
