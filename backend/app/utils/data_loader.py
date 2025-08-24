import csv, os, math
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

class DataStore:
    def __init__(self):
        self.products = self._load_csv(DATA_DIR / "products.csv")
        self.inventory = self._load_csv(DATA_DIR / "inventory.csv")
        self._index = {p['id']: p for p in self.products}

    def _load_csv(self, path):
        with open(path, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            return [dict(row) for row in reader]

    def get_product(self, product_id):
        p = self._index.get(product_id)
        if not p:
            return None
        # cast numeric fields
        p = dict(p)
        p['cost'] = float(p['cost'])
        p['base_price'] = float(p['base_price'])
        p['ttl_days'] = int(p['ttl_days'])
        return p
