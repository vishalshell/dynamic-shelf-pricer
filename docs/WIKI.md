# DSP Wiki — How the System Works

This document explains the **data flow**, **pricing math**, and **guardrails**.

---

## 1) Data flow

1. Load product economics from `products.csv` (cost, base price, TTL).
2. Load inventory and (optionally) synthetic sales history.
3. If `app/models/demand_model.joblib` exists, load it.
4. API receives a pricing request with context (days_to_expiry, inventory, competitor_price, etc.).
5. Pricing engine:
   - Computes **freshness** = `max(0, min(1, days_left / ttl_days))`.
   - Estimates **demand**:
     - **ML path**: `demand_hat = model.predict(X)`
     - **Rule path**: `demand_hat = baseline - b_price*price + b_comp*comp_price - b_exp*(1-freshness) + ...`
   - Chooses price `p` that maximizes `Revenue(p) - SpoilageCost(p)` subject to guardrails.
6. Return the recommended price + a human-readable explanation.

---

## 2) Objective and pricing logic

We maximize **expected profit** over the next step (or short horizon) by balancing margin and spoilage:

- `revenue(p) = p * min(inventory, demand_hat(p))`
- `spoilage_cost(p) = unit_cost * max(0, inventory - demand_hat(p))`
- `objective(p) = revenue(p) - spoilage_cost(p)`

We search over a feasible price grid between **floor** and **ceiling** and pick the `p` that maximizes the objective.

### Demand curve (rule-based fallback)

We use a simple, interpretable form:

```
demand_hat(p) = max(0,
    alpha * base_demand
  - beta_price * (p - base_price)
  + beta_comp * max(0, competitor_price - p)
  - beta_expiry * (1 - freshness)
  + beta_promo * promo_flag
  + beta_weather * weather_score_adjustment
)
```

- `freshness = days_left / ttl_days`
- `weather_score_adjustment` can lift salads/berries demand on hot days, etc.
- Coefficients are product-class specific (see `pricing.py`).

### Guardrails

- **Floor**: `floor = max(cost * (1 + min_margin_pct), min_floor_abs)`
- **Ceiling**: `ceiling = min(base_price * 1.5, max_ceiling_abs)`
- Enforced hard — if the argmax falls outside, we clamp to `[floor, ceiling]`.

### Explainability

- We return key drivers (e.g., *low freshness*, *high inventory*) in the `explanation` field.
- Model or rule weights are logged to help retail ops trust the system.

---

## 3) Simulation

We simulate day-by-day:

1. For each day: compute `days_to_expiry`, call the pricing engine for `price_t`.
2. Sample realized demand: `min(inventory_t, demand_hat(price_t) + noise)`.
3. Update inventory and accumulate revenue/spoilage.
4. Return KPIs (revenue, sell-through, spoilage).

This is intentionally simple; extend to multi-period horizon with markdown schedules.

---

## 4) Extensions

- **Bayesian demand** or **quantile regression** to price to a service level.
- Store/cluster-specific policy with market signals (POS, promos, events).
- **A/B testing** harness to compare static vs. dynamic policies.
- **Audit log** to meet governance requirements (who/what/why).

---

## 5) Ethics & compliance

- Respect regulatory constraints (price floors/anti-gouging).
- Avoid unstable price oscillations; smooth with dampening or cadence rules.
- Provide **human override** paths.
