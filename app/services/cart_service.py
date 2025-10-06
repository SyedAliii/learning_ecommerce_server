from ..schemas.cart import (CartAddRequest, CartRemoveRequest)
from ..schemas.generic import GenericResponse
from ..models.cart_products import CartProducts
from ..models.cart import Cart
from ..models.user import User
from fastapi import status
from sqlalchemy.orm import Session
from ..core.exceptions.exception_main import GenericException

class CartService:
    def __init__(self, db: Session):
        self.db = db
    
    def __check_cart_exists_in_cart_products(self, cart_id: int):
        cart_product = self.db.query(CartProducts).filter(CartProducts.cart_id == cart_id).first()
        return cart_product
    
    def __check_product_exists_in_cart_products(self, cart_id: int, product_id: str):
        cart_product = self.db.query(CartProducts).filter(CartProducts.cart_id == cart_id,
                                                          CartProducts.product_id == product_id).first()
        return cart_product
    
    def __update_only_quantity_in_cart_products(self, cart_product: CartProducts, quantity: int, decrease: bool):
        if decrease:
            cart_product.quantity -= quantity
        else:
            cart_product.quantity += quantity
        
        if cart_product.quantity < 1:
            self.db.delete(cart_product)

        self.db.commit()
        return GenericResponse(
                status_code=status.HTTP_200_OK,
                msg=f"Product quantity updated in cart"
            )
    
    def __add_new_product_to_cart_products(self, cart_id: int, product_id: str, quantity: int):
        new_cart_product = CartProducts()
        new_cart_product.cart_id = cart_id
        new_cart_product.product_id = product_id
        new_cart_product.quantity = quantity
        self.db.add(new_cart_product)
        self.db.commit()
        return GenericResponse(
                status_code=status.HTTP_201_CREATED,
                msg=f"Product added to cart"
            )

    def __add_new_cart(self, user_id: int):
        new_cart = Cart()
        new_cart.user_id = user_id
        self.db.add(new_cart)
        self.db.commit()
        return new_cart.id

    def add(self, cart_add_request: CartAddRequest, user_id: int):
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            if user.active_cart_id != None:
                    if self.__check_cart_exists_in_cart_products(user.active_cart_id):
                        cart_product = self.__check_product_exists_in_cart_products(user.active_cart_id, 
                                                                                  cart_add_request.product_id)
                        if cart_product:
                            return self.__update_only_quantity_in_cart_products(cart_product, cart_add_request.quantity, False)
                        else:
                            return self.__add_new_product_to_cart_products(user.active_cart_id, cart_add_request.product_id, cart_add_request.quantity)
                    else:
                        return self.__add_new_product_to_cart_products(user.active_cart_id, cart_add_request.product_id, cart_add_request.quantity)
            else:
                user.active_cart_id = self.__add_new_cart(user.id)
                return self.__add_new_product_to_cart_products(user.active_cart_id, cart_add_request.product_id, cart_add_request.quantity)
        except GenericException:
            raise
        except Exception as e:
            self.db.rollback()
            raise GenericException(reason=str(e))
        
    def remove(self, req: CartRemoveRequest, user_id: int):
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            if user.active_cart_id != None:
                if self.__check_cart_exists_in_cart_products(user.active_cart_id):
                    cart_product = self.__check_product_exists_in_cart_products(user.active_cart_id, 
                                                                                req.product_id)
                    if cart_product:
                        if cart_product.quantity > 1:
                            return self.__update_only_quantity_in_cart_products(cart_product, req.quantity, True)
                        else:
                            self.db.delete(cart_product)
                            self.db.commit()
                            return GenericResponse(
                                status_code=status.HTTP_200_OK,
                                msg=f"Product removed from cart"
                            )
                    else:
                        return GenericResponse(
                            status_code=status.HTTP_204_NO_CONTENT,
                            msg=f"No products in cart to remove"
                        )
                else:
                    return GenericResponse(
                        status_code=status.HTTP_204_NO_CONTENT,
                        msg=f"No cart exist to remove products from"
                    )
            else:
                user.active_cart_id = self.__add_new_cart(user.id)
                return GenericResponse(
                    status_code=status.HTTP_204_NO_CONTENT,
                    msg=f"No active cart"
                )
        except GenericException:
            raise
        except Exception as e:
            self.db.rollback()
            raise GenericException(reason=str(e))
        
    def delete(self, user_id: int):
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            user.active_cart_id = None
            self.db.commit()
            return GenericResponse(
                status_code=status.HTTP_200_OK,
                msg=f"Cart deleted successfully"
            )
        except GenericException:
            raise
        except Exception as e:
            self.db.rollback()
            raise GenericException(reason=str(e))