# API

Base: `http://localhost:8000`

## `GET /api/products`
Returns the product catalog with base economics.

## `POST /api/recommend`
Body:
```json
{
  "product_id": "milk-1L",
  "context": {
    "days_to_expiry": 2,
    "inventory": 40,
    "competitor_price": 6.5,
    "promo_flag": false,
    "weather_score": 0.4
  }
}
```
Response:
```json
{
  "product_id": "milk-1L",
  "recommended_price": 5.90,
  "explanation": "Lowering price due to low freshness and high inventory.",
  "inputs": {...},
  "guardrails": {"floor": 5.0, "ceiling": 8.5, "min_margin_pct": 0.1}
}
```

## `POST /api/simulate`
Run a simple day-by-day simulation.
Body:
```json
{ "days": 7, "policy": "dynamic" }  // "static" or "dynamic"
```
Response: revenue, spoilage, average price, etc.

## `POST /api/train` (optional)
Fits a linear demand model on the synthetic data (requires scikit-learn). Saves to `app/models/demand_model.joblib`.
