from app.models.cart import Cart
from ..schemas.user import UserCreateRequest, UserAuthenticateRequest, UserAuthenticateResponse, UserResponse
from ..schemas.generic import GenericResponse
from ..models.user import User, UserRole
from fastapi import Depends, status
from sqlalchemy.orm import Session
from ..core.exceptions.exception_main import GenericException
from ..core.security import verify_password, get_password_hash
from ..core.config import settings

class UserService:
    def __init__(self, db: Session):
        self.db = db

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
