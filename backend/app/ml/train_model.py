# Optional: trains a tiny linear demand model on synthetic data
# and saves to app/models/demand_model.joblib
import pandas as pd
import joblib
from sklearn.linear_model import LinearRegression
from pathlib import Path

DATA = Path(__file__).resolve().parents[1] / "data" / "synthetic_sales.csv"
MODEL = Path(__file__).resolve().parents[1] / "models" / "demand_model.joblib"

def main():
    df = pd.read_csv(DATA)
    features = ["price", "inventory", "days_to_expiry", "competitor_price", "promo_flag", "weather_score"]
    df["promo_flag"] = df["promo_flag"].astype(int)
    df = df.fillna(0.0)
    X = df[features]
    y = df["units_sold"]
    model = LinearRegression().fit(X, y)
    MODEL.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, MODEL)
    print("Saved model to", MODEL)

if __name__ == "__main__":
    main()
