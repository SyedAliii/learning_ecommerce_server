from ....schemas.cart import (CartAddRequest)
from ....schemas.generic import GenericResponse
from fastapi import APIRouter, Depends
from ....services.cart_service import CartService
from ....db.session import get_db
from sqlalchemy.orm import Session
from ...deps import get_current_user
from typing import Optional
from fastapi import Request, HTTPException

router = APIRouter()

@router.post("/create_order", response_model=GenericResponse)
async def create_order(cart_add_request: CartAddRequest, user_id: Optional[int] = Depends(get_current_user), db: Session = Depends(get_db)):
    cart_service = CartService(db)
    return cart_service.add(cart_add_request, user_id)

@router.post("/update_order", response_model=GenericResponse)
async def update_order(cart_add_request: CartAddRequest, user_id: Optional[int] = Depends(get_current_user), db: Session = Depends(get_db)):
    cart_service = CartService(db)
    return cart_service.remove(cart_add_request, user_id)

