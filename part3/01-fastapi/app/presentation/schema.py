from typing import List

from pydantic import BaseModel, Field

from app.domain.models import Product


class OrderUpdate(BaseModel):
    products: List[Product] = Field(default_factory=list)
