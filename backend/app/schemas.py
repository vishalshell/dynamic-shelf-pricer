from pydantic import BaseModel, Field
from typing import Optional

class PricingContext(BaseModel):
    days_to_expiry: int = Field(..., ge=0)
    inventory: int = Field(..., ge=0)
    competitor_price: Optional[float] = None
    promo_flag: bool = False
    weather_score: float = 0.0  # 0..1

class PricingRequest(BaseModel):
    product_id: str
    context: PricingContext

class SimulationRequest(BaseModel):
    days: int = Field(7, ge=1, le=60)
    policy: str = "dynamic"  # or "static"
