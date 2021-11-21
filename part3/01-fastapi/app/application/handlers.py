import asyncio
from typing import Optional, List, Dict, Any
from uuid import UUID

from fastapi import UploadFile

from app.adapters.repository import Repository
from app.domain.models import Order, OrderStatus, Product
from app.application.model import predict_from_image_byte


def get_order_by_id(order_id: UUID, repository: Repository) -> Optional[Order]:
    """
    Order ID로 Order를 조회합니다

    Args:
        order_id (UUID): order id
        repository (Repository): repository

    Returns:
        Optional[Order]:

    """
    return repository.get(ref=order_id)


def update_order_by_id(
    order_id: UUID, products: List[Product], repository: Repository
) -> Optional[Order]:
    """
    Order를 업데이트 합니다

    Args:
        order_id (UUID): order id
        products (List[Product]): products
        repository (Repository): repository

    Returns:
        Optional[Order]: 업데이트 된 Order 또는 None
    """
    existing_order = get_order_by_id(order_id=order_id, repository=repository)
    if not existing_order:
        return

    updated_order = existing_order.copy()
    for next_product in products:
        updated_order = existing_order.add_product(next_product)
    return updated_order


async def get_prediction_result(
    order_id: UUID,
    model: "MyEfficientNet",
    config: Dict[str, Any],
    repository: Repository,
):
    order = get_order_by_id(order_id=order_id, repository=repository)
    order.update_status(status=OrderStatus.IN_PROGRESS)
    await asyncio.sleep(3)
    for product in order.products:
        if not getattr(product, "input_image"):
            continue
        input_image: UploadFile = product.input_image
        image_bytes = await input_image.read()
        inference_result = predict_from_image_byte(
            image_bytes=image_bytes, model=model, config=config
        )
        product.update_output(output=inference_result)
    order.update_status(status=OrderStatus.DONE)
    return update_order_by_id(
        order_id=order_id, products=order.products, repository=repository
    ).id
