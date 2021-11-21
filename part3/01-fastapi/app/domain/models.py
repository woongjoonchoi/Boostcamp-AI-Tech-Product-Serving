from datetime import datetime
from enum import IntEnum
from typing import Any, Optional, List
from uuid import UUID, uuid4

from fastapi import UploadFile
from pydantic import BaseModel, Field


class Product(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    name: str
    price: float
    output: Any
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    def update_output(self, output) -> ...:
        ...


class InferenceImageProduct(Product):
    name: str = "inference_image_product"
    price: float = 100.0
    input_image: UploadFile
    output: Optional[List]

    def update_output(self, output) -> None:
        self.output = output
        self.updated_at = datetime.now()

    class Config:
        arbitrary_types_allowed = True


class OrderStatus(IntEnum):
    PENDING = 0
    IN_PROGRESS = 1
    DONE = 2


class Order(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    products: List[Product] = Field(default_factory=list)
    status: OrderStatus
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    @property
    def bill(self) -> int:
        return sum([product.price for product in self.products])

    def add_product(self, product: Product) -> "Order":
        if product.id in [existing_product.id for existing_product in self.products]:
            return self

        self.products.append(product)
        self.updated_at = datetime.now()
        return self

    def update_status(self, status: OrderStatus) -> None:
        self.status = status
        self.updated_at = datetime.now()