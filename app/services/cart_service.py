from app.models.product_image import ProductImage
from app.schemas.cart import (CartAddRequest, CartRemoveRequest, CartViewResponse)
from app.schemas.generic import GenericResponse
from app.models.cart_products import CartProducts
from app.models.cart import Cart
from app.models.user import User
from app.models.product import Product
from fastapi import status
from sqlalchemy.orm import Session
from app.core.exceptions.exception_main import GenericException
from app.schemas.product import ProductBaseModel
from typing import List

from app.schemas.user import UserCartProduct

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
        product = self.db.query(Product).filter(Product.id == product_id).first()
        if product.quantity < quantity:
            raise GenericException(reason=f"Unable to add product: Low Stock")

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
        
    def view_cart(self, user_id: int):
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            if user.active_cart_id != None:
                cart_products = self.db.query(CartProducts).filter(CartProducts.cart_id == user.active_cart_id).all()
                products = self.db.query(Product).filter(Product.id.in_([cp.product_id for cp in cart_products])).all()
                
                user_cart_products: List[UserCartProduct] = []
                for product in products:
                    user_cart_product = UserCartProduct(
                        id=product.id,
                        title=product.title,
                        description=product.description,
                        price=product.price,
                        total_quantity=product.quantity,
                        category=product.category_id,
                        subcategory=product.subcategory_id,
                        quantity_in_cart=next((cp.quantity for cp in cart_products if cp.product_id == product.id), 0)
                    )
                    user_cart_products.append(user_cart_product)
                
                return CartViewResponse(
                    products=user_cart_products,
                    status_code=status.HTTP_200_OK,
                    msg=f"Cart retrieved successfully"
                )
            else:
                return GenericResponse(
                    status_code=status.HTTP_204_NO_CONTENT,
                    msg=f"No active cart"
                )
        except GenericException:
            raise
        except Exception as e:
            self.db.rollback()
            raise GenericException(reason=str(e))