from typing import List
from app.models.cart import Cart
from app.models.cart_products import CartProducts
from app.models.product import Product
from app.schemas.user import UserCreateRequest, UserAuthenticateRequest, UserAuthenticateResponse, UserResponse, UserDataResponse, UserCartProduct
from app.schemas.generic import GenericResponse
from app.schemas.product import ProductBaseModel
from app.models.user import User, UserRole
from fastapi import Depends, status
from sqlalchemy.orm import Session
from app.core.exceptions.exception_main import GenericException
from app.core.security import verify_password, get_password_hash
from app.core.config import settings

class UserService:
    def __init__(self, db: Session):
        self.db = db

    def __get_product_ids_in_cart(self, cart_id: int):
        try:
            cart_products_ids = self.db.query(CartProducts).filter(CartProducts.cart_id == cart_id).all()
            return cart_products_ids
        except Exception as e:
            raise GenericException(reason=str(e))
        
    def __get_user_cart_products(self, cart_products_ids: List[CartProducts]):
        products: List[Product] = []
        for cart_product in cart_products_ids:
            product = self.db.query(Product).filter(Product.id == cart_product.product_id).first()
            if product:
                products.append(product)

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
                quantity_in_cart=next((cp.quantity for cp in cart_products_ids if cp.product_id == product.id), 0)
            )
            user_cart_products.append(user_cart_product)
        return user_cart_products

    def create_admin(self, user_create_request: UserCreateRequest):
        try:
            new_user = User()
            new_user.name = user_create_request.name
            new_user.email = user_create_request.email
            new_user.address = user_create_request.address
            new_user.city = user_create_request.city
            new_user.country = user_create_request.country
            new_user.roles = UserRole.ADMIN
            new_user.hashed_password = get_password_hash(user_create_request.password)
            
            self.db.add(new_user)
            
            self.db.commit()
            self.db.refresh(new_user)

            return GenericResponse(
                status_code=status.HTTP_201_CREATED,
                msg=f"User Id: {new_user.id} with role Admin successfully created"
            )
        except Exception as e:
            self.db.rollback()
            raise GenericException(reason=str(e))

    def create_user(self, user_create_request: UserCreateRequest):
        try:
            new_user = User()
            new_user.name = user_create_request.name
            new_user.email = user_create_request.email
            new_user.address = user_create_request.address
            new_user.city = user_create_request.city
            new_user.country = user_create_request.country
            new_user.roles = UserRole.USER
            new_user.hashed_password = get_password_hash(user_create_request.password)
            
            self.db.add(new_user)
            self.db.commit()
            self.db.refresh(new_user)

            return GenericResponse(
                status_code=status.HTTP_201_CREATED,
                msg=f"User Id: {new_user.id} with role User successfully created"
            )
        except Exception as e:
            self.db.rollback()
            raise GenericException(reason=str(e))
        
    def delete(self, user_id_to_delete: int, user_id: int):
        try:
            if user_id is None:
                raise GenericException(reason="User not authenticated")
            
            user = self.db.query(User).filter(User.id == user_id).first()
            if user.roles != UserRole.ADMIN:
                raise GenericException(reason="User not authorized to delete users")

            user_to_delete = self.db.query(User).filter(User.id == user_id_to_delete).first()
            if not user_to_delete:
                raise GenericException(reason="User not found")

            self.db.delete(user_to_delete)
            self.db.commit()

            return GenericResponse(
                status_code=status.HTTP_200_OK,
                msg=f"User Id: {user_id} successfully deleted"
            )
        except Exception as e:
            self.db.rollback()
            raise GenericException(reason=str(e))
        
    def authenticate(self, req: UserAuthenticateRequest):
        try:
            user = self.db.query(User).filter(User.email == req.email).first()
            if not user or not verify_password(req.password, user.hashed_password):
                return UserAuthenticateResponse(status_code=status.HTTP_404_NOT_FOUND, msg="Invalid email or password")
            
            return UserAuthenticateResponse(
                    status_code=status.HTTP_200_OK,
                    msg="User authenticated successfully",
                    user=UserResponse(id=user.id, name=user.name, email=user.email, address=user.address, city=user.city, country=user.country, roles=user.roles)
                )
        except Exception as e:
            raise GenericException(reason=str(e))

    def get_user_data(self, access_token: str, user_id: int):
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            product_ids_in_cart = self.__get_product_ids_in_cart(user.active_cart_id) if user.active_cart_id else []
            return UserDataResponse(
                access_token=access_token,
                name=user.name,
                email=user.email,
                roles=user.roles,
                cart_products=self.__get_user_cart_products(product_ids_in_cart),
                status_code=status.HTTP_200_OK,
                msg=f"User Successfully Logged In"
            )
        except GenericException:
            raise
        except Exception as e:
            self.db.rollback()
            raise GenericException(reason=str(e))