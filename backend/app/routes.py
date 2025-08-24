from fastapi import APIRouter, HTTPException
from .schemas import PricingRequest, SimulationRequest
from .utils.data_loader import DataStore
from .pricing import PriceEngine

router = APIRouter()

datastore = DataStore()
engine = PriceEngine(datastore=datastore)

@router.get("/products")
def get_products():
    return datastore.products

@router.post("/recommend")
def recommend(req: PricingRequest):
    product = datastore.get_product(req.product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    rec = engine.recommend_price(product, req.context.dict())
    return rec

@router.post("/simulate")
def simulate(req: SimulationRequest):
    return engine.simulate(days=req.days, policy=req.policy)
