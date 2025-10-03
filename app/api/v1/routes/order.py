from ....schemas.order import (OrderUpdateRequest)
from ....schemas.generic import GenericResponse
from fastapi import APIRouter, Depends
from ....services.order_service import OrderService
from ....db.session import get_db
from sqlalchemy.orm import Session
from ...deps import get_current_user
from typing import Optional

router = APIRouter()

@router.post("/create_order", response_model=GenericResponse)
async def create_order(user_id: Optional[int] = Depends(get_current_user), db: Session = Depends(get_db)):
    order_service = OrderService(db)
    return order_service.create(user_id)

@router.post("/update_order", response_model=GenericResponse)
async def update_order(order_update_request: OrderUpdateRequest, user_id: Optional[int] = Depends(get_current_user), db: Session = Depends(get_db)):
    order_service = OrderService(db)
    return order_service.update(order_update_request, user_id)

