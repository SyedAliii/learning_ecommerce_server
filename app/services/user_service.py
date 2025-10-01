from datetime import datetime, timedelta
from ..schemas.user import UserCreateRequest, UserCreateResponse, UserAuthenticateRequest, UserAuthenticateResponse, UserResponse
from ..models.users import User
from fastapi import Depends, status
from sqlalchemy.orm import Session
from ..core.exceptions.user_handlers import UserNotCreatedException, AuthFailedException
from ..core.security import verify_password, get_password_hash
from ..core.config import settings

class UserService:
    def __init__(self, db: Session):
        self.db = db

    def create(self, user_create_request: UserCreateRequest):
        try:
            new_user = User()
            new_user.id = user_create_request.id
            new_user.name = user_create_request.name
            new_user.email = user_create_request.email
            new_user.address = user_create_request.address
            new_user.city = user_create_request.city
            new_user.country = user_create_request.country
            new_user.roles = user_create_request.roles
            new_user.hashed_password = get_password_hash(user_create_request.password)
            
            self.db.add(new_user)
            self.db.commit()
            self.db.refresh(new_user)

            return UserCreateResponse(
                status_code=status.HTTP_201_CREATED,
                msg=f"User Id: {new_user.id} successfully created"
            )
        except Exception as e:
            self.db.rollback()
            raise UserNotCreatedException(user_id=user_create_request.id, reason=str(e))
        
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
            raise AuthFailedException(email=req.email, reason=str(e))
