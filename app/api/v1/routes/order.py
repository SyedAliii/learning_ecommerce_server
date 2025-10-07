from app.schemas.order import (OrderConfirmResponse, OrderShippedRequest, OrderShippedResponse, OrderDeliveredRequest, OrderDeliveredResponse)
from app.schemas.generic import GenericResponse
from fastapi import APIRouter, Depends
from app.services.order_service import OrderService
from app.db.session import get_db
from sqlalchemy.orm import Session
from app.api.deps import get_current_user
from typing import Optional

router = APIRouter()

@router.post("/create_order", response_model=GenericResponse)
async def create_order(user_id: Optional[int] = Depends(get_current_user), db: Session = Depends(get_db)):
    order_service = OrderService(db)
    return order_service.create(user_id)

@router.post("/confirm_order", response_model=OrderConfirmResponse)
async def confirm_order(user_id: Optional[int] = Depends(get_current_user), db: Session = Depends(get_db)):
    order_service = OrderService(db)
    return order_service.confirm(user_id)

@router.post("/shipped_order", response_model=OrderShippedResponse)
async def shipped_order(order_shipped_request: OrderShippedRequest, user_id: Optional[int] = Depends(get_current_user), db: Session = Depends(get_db)):
    order_service = OrderService(db)
    return order_service.shipped(order_shipped_request, user_id)

@router.post("/delivered_order", response_model=OrderDeliveredResponse)
async def delivered_order(order_delivered_request: OrderDeliveredRequest, user_id: Optional[int] = Depends(get_current_user), db: Session = Depends(get_db)):
    order_service = OrderService(db)
    return order_service.delivered(order_delivered_request, user_id)

