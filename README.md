# Dynamic Shelf Pricer (DSP)

A **reference implementation** that shows how to use AI to manage **dynamic pricing** for perishable goods on retail shelves.
Built with a **Python FastAPI** backend and a **React (Vite)** frontend. Includes **temporary test data** and a
simple **pricing engine** that can run with or without a trained ML model.

---

## What it does

- **Recommends prices** for perishable SKUs based on *shelf life left, inventory, demand forecast, competitor price,* and guardrails.
- **Simulates** 7–30 days of shelf operations to compare static vs. dynamic pricing policies.
- Ships with **seed data** for common perishables (milk, yogurt, bread, salads, berries, chicken, sushi, cut fruit).
- **Works even without ML**: falls back to an interpretable rule-based engine if no model is trained yet.
- **API-first**: clean FastAPI endpoints, ready for POS/inventory systems.
- **Basic React UI**: browse products, tweak context, and get live price recommendations.

---

## Architecture (high-level)

```
React (Vite) UI  --->  FastAPI (pricing endpoints)  --->  Pricing Engine
        |                         |                         |--- Rule-based logic
        |                         |                         |--- Optional ML demand model (scikit-learn)
        |                         |                         |--- Guardrails (floors/ceilings/margins)
        v                         v
      User                   Data loaders
  (simulate, price)     (CSV seed in /backend/app/data)
```

---

## Quickstart

### 1) Backend

```bash
cd backend
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8000
```

### 2) Frontend

```bash
cd frontend
npm install
npm run dev  # dev server
# or
npm run build && npm run preview
```

Open the UI at the URL that Vite prints (http://localhost:5173). The backend defaults to http://localhost:8000.

---

## Data

Seed CSVs live in `backend/app/data`:

- `products.csv` — product catalog & economics (cost/base_price/TTL)
- `inventory.csv` — daily starting inventory
- `synthetic_sales.csv` — toy data to train a simple demand model (optional)

Use the UI or curl the API to get recommendations. You can also run `python app/ml/train_model.py`
to fit a basic linear model on the synthetic data and save it to `app/models/demand_model.joblib`.
If no model exists, DSP uses a well-documented rule-based fallback.

---

## Configuration

- `backend/.env` — CORS origins, port, model path, etc.
- `frontend/.env` — API base URL

### Backend env (`.env.example`)

```
PORT=8000
CORS_ORIGINS=http://localhost:5173
MODEL_PATH=app/models/demand_model.joblib
```

### Frontend env (`frontend/.env`)

```
VITE_API_BASE=http://localhost:8000
```

---

## API Surface

See **[docs/API.md](docs/API.md)** for endpoints and examples.

---

## How pricing works (short version)

- Compute a **freshness** factor from days-to-expiry vs. TTL.
- Estimate **demand** (either via ML model or rule-of-thumb elasticity).
- Choose a price that maximizes **expected revenue – expected spoilage cost**, subject to **guardrails** (min margin, floor, ceiling).
- Optionally nudge toward **competitor price** while protecting margin.

The **full explanation** with formulas/pseudocode is in **[docs/WIKI.md](docs/WIKI.md)**.

---

## Run with Docker (optional)

```bash
docker compose up --build
```

The compose file starts both backend (FastAPI) and frontend (Vite preview).

---

## Roadmap

- [ ] Bayesian demand model w/ uncertainty bands
- [ ] Multi-store policy learning (per cluster, per hour)
- [ ] Real-time signals (POS feed, shelf sensors, weather)
- [ ] A/B testing harness & offline evaluation
- [ ] Policy guardrail DSL + audit logs

---

## License

MIT — see [LICENSE](LICENSE).

---

## Attribution & Credits
Contributions welcome — see [CONTRIBUTING.md](CONTRIBUTING.md).
