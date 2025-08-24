import math, random
from typing import Dict, Any, List
from .utils.data_loader import DataStore

class PriceEngine:
    def __init__(self, datastore: DataStore):
        self.ds = datastore

    def _guardrails(self, product, min_margin_pct=0.10, floor_abs=None, ceiling_abs=None):
        floor = max(product['cost'] * (1 + min_margin_pct), floor_abs or 0.01)
        ceiling = min(product['base_price'] * 1.5, ceiling_abs or product['base_price'] * 2.0)
        return floor, ceiling

    def _baseline_demand(self, product):
        # Very simple per-category baseline
        cat = product['category'].lower()
        base = 50
        if cat in ('dairy', 'bakery'):
            base = 60
        elif cat in ('produce', 'ready-to-eat'):
            base = 40
        elif cat in ('meat', 'seafood'):
            base = 30
        return base

    def _rule_demand(self, product, price, ctx):
        base = self._baseline_demand(product)
        base_price = product['base_price']
        ttl = product['ttl_days']
        freshness = max(0.0, min(1.0, ctx['days_to_expiry'] / max(1, ttl)))
        comp = ctx.get('competitor_price')
        promo = 1.0 if ctx.get('promo_flag') else 0.0
        weather = float(ctx.get('weather_score', 0.0))

        # Coefficients — tune per category if needed
        beta_price = 6.0    # price sensitivity
        beta_comp  = 2.5    # competitor undercut bonus
        beta_exp   = 30.0   # penalty for staleness
        beta_promo = 8.0
        beta_weather = 5.0 if product['category'].lower() in ('produce', 'ready-to-eat') else 1.0

        val = (
            base
            - beta_price * max(0.0, price - base_price)
            + (beta_comp * max(0.0, (comp - price))) if comp else 0.0
        )

        # freshness penalty (lower freshness → lower demand unless price drops)
        val -= beta_exp * (1.0 - freshness)
        val += beta_promo * promo
        val += beta_weather * weather

        return max(0.0, val)

    def recommend_price(self, product: Dict[str, Any], ctx: Dict[str, Any]) -> Dict[str, Any]:
        floor, ceiling = self._guardrails(product)
        inv = max(0, int(ctx['inventory']))
        best = None

        # search a discrete price grid
        step = max(0.05, product['base_price'] * 0.01)
        grid = [round(p, 2) for p in frange(floor, ceiling, step)]

        explanation = []

        for p in grid:
            demand = self._rule_demand(product, p, ctx)
            sales = min(inv, demand)
            revenue = p * sales
            spoilage_cost = product['cost'] * max(0.0, inv - sales)
            objective = revenue - spoilage_cost
            if (best is None) or (objective > best['objective']):
                best = dict(price=p, demand=demand, revenue=revenue,
                            spoilage_cost=spoilage_cost, objective=objective)

        # explanation heuristics
        if ctx['days_to_expiry'] <= 1:
            explanation.append("Low freshness → markdown to move stock")
        if inv > self._baseline_demand(product):
            explanation.append("High inventory → price favors sell-through")
        if ctx.get('competitor_price') and best['price'] < ctx['competitor_price']:
            explanation.append("Undercutting competitor while protecting margin")
        if not explanation:
            explanation.append("Standard optimization within guardrails")

        return {
            "product_id": product['id'],
            "recommended_price": round(best['price'], 2),
            "expected_demand": round(best['demand'], 1),
            "expected_revenue": round(best['revenue'], 2),
            "expected_spoilage_cost": round(best['spoilage_cost'], 2),
            "inputs": {
                "inventory": inv,
                "days_to_expiry": ctx['days_to_expiry'],
                "competitor_price": ctx.get('competitor_price'),
                "promo_flag": ctx.get('promo_flag', False),
                "weather_score": ctx.get('weather_score', 0.0),
            },
            "guardrails": {
                "floor": round(floor, 2),
                "ceiling": round(ceiling, 2),
                "min_margin_pct": 0.10
            },
            "explanation": "; ".join(explanation)
        }

    def simulate(self, days: int = 7, policy: str = "dynamic"):
        # naive simulation over all products
        out = []
        for p in self.ds.products:
            prod = dict(p)
            prod['cost'] = float(prod['cost']); prod['base_price'] = float(prod['base_price']); prod['ttl_days'] = int(prod['ttl_days'])
            inv = 50  # start inventory
            ttl = prod['ttl_days']
            revenue = 0.0
            spoilage = 0.0
            for d in range(days):
                days_left = max(0, ttl - d - 1)
                if policy == "static":
                    ctx = {"days_to_expiry": days_left, "inventory": inv, "competitor_price": None, "promo_flag": False, "weather_score": 0.0}
                    price = prod['base_price']
                    demand = self._rule_demand(prod, price, ctx)
                else:
                    ctx = {"days_to_expiry": days_left, "inventory": inv, "competitor_price": None, "promo_flag": False, "weather_score": 0.0}
                    rec = self.recommend_price(prod, ctx)
                    price = rec['recommended_price']
                    demand = rec['expected_demand']

                sales = min(inv, demand)
                revenue += price * sales
                inv = max(0.0, inv - sales)

            # leftover becomes spoilage at end
            spoilage += prod['cost'] * inv
            out.append({
                "product_id": prod['id'],
                "policy": policy,
                "days": days,
                "revenue": round(revenue, 2),
                "spoilage_cost": round(spoilage, 2)
            })
        return {"results": out}

def frange(start, stop, step):
    x = start
    while x <= stop + 1e-9:
        yield x
        x += step
