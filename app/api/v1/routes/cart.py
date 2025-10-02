from ....schemas.cart import (CartAddRequest)
from ....schemas.generic import GenericResponse
from fastapi import APIRouter, Depends
from ....services.cart_service import CartService
from ....db.session import get_db
from sqlalchemy.orm import Session
from ...deps import get_current_user

router = APIRouter()

@router.post("/add_to_cart", response_model=GenericResponse)
async def add_cart(cart_add_request: CartAddRequest, user_id: int = Depends(get_current_user), db: Session = Depends(get_db)):
    cart_service = CartService(db)
    return cart_service.add(cart_add_request, user_id)

@router.post("/remove_from_cart", response_model=GenericResponse)
async def remove_cart(cart_add_request: CartAddRequest, user_id: int = Depends(get_current_user), db: Session = Depends(get_db)):
    cart_service = CartService(db)
    return cart_service.remove(cart_add_request, user_id)

@router.post("/delete_cart", response_model=GenericResponse)
async def delete_cart(user_id: int = Depends(get_current_user), db: Session = Depends(get_db)):
    cart_service = CartService(db)
    return cart_service.delete(user_id)
