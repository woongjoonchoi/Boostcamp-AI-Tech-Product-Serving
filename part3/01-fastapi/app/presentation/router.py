from typing import List, Union, Dict, Any
from uuid import UUID

from fastapi import APIRouter, UploadFile, File, Depends
from starlette.background import BackgroundTasks

from app.adapters.repository import InMemoryRepository, Repository
from app.application.handlers import (
    get_order_by_id,
    get_prediction_result,
    update_order_by_id,
)
from app.domain.models import Order, InferenceImageProduct, OrderStatus
from app.application.model import MyEfficientNet, get_model, get_config
from app.presentation.schema import OrderUpdate

router = APIRouter()


def get_repository():
    return InMemoryRepository()


@router.get("/order", description="주문 리스트를 가져옵니다")
async def get_orders(repository: Repository = Depends(get_repository)) -> List[Order]:
    return repository.get_all()


@router.get("/order/{order_id}", description="주문 정보를 가져옵니다")
async def get_order(
    order_id: UUID, repository: Repository = Depends(get_repository)
) -> Union[Order, dict]:
    order = get_order_by_id(order_id=order_id, repository=repository)
    if not order:
        return {"message": "주문 정보를 찾을 수 없습니다"}
    return order


@router.post("/order", description="주문을 요청합니다")
async def make_order(
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(...),
    model: MyEfficientNet = Depends(get_model),
    config: Dict[str, Any] = Depends(get_config),
    repository: Repository = Depends(get_repository),
) -> Union[UUID, dict]:
    new_order = Order(
        products=[InferenceImageProduct(input_image=file) for file in files],
        status=OrderStatus.PENDING,
    )
    background_tasks.add_task(
        get_prediction_result,
        order_id=new_order.id,
        model=model,
        config=config,
        repository=repository,
    )
    repository.add(new_order)
    return new_order.id


@router.patch("/order/{order_id}", description="주문을 수정합니다")
async def update_order(
    order_id: UUID,
    order_update: OrderUpdate,
    repository: Repository = Depends(get_repository),
) -> Union[Order, dict]:
    updated_order = update_order_by_id(
        order_id=order_id, products=order_update.products, repository=repository
    )
    if not updated_order:
        return {"message": "주문 정보를 찾을 수 없습니다"}
    return updated_order


@router.get("/bill/{order_id}", description="계산을 요청합니다")
async def get_bill(
    order_id: UUID, repository: Repository = Depends(get_repository)
) -> Union[float, dict]:
    found_order = get_order_by_id(order_id=order_id, repository=repository)
    if not found_order:
        return {"message": "주문 정보를 찾을 수 없습니다"}
    return found_order.bill
