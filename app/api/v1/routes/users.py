from app.schemas.user import UserCreateRequest, UserDataResponse
from app.schemas.generic import GenericResponse
from fastapi import APIRouter, Depends
from app.services.user_service import UserService
from app.db.session import get_db
from sqlalchemy.orm import Session
from app.schemas.user import UserAuthenticateRequest
from fastapi import APIRouter, Depends
from app.services.user_service import UserService
from app.db.session import get_db
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from app.core.security import create_access_token

router = APIRouter()

@router.post("/create_admin", response_model=GenericResponse)
async def create_admin(user_create_request: UserCreateRequest, db: Session = Depends(get_db)):
    user_service = UserService(db)
    return user_service.create_admin(user_create_request)

@router.post("/create_user", response_model=UserDataResponse)
async def create_user(user_create_request: UserCreateRequest, db: Session = Depends(get_db)):
    user_service = UserService(db)
    response = user_service.create_user(user_create_request)
    if not response.status_code == 201:
        return response
    else:
        token = create_access_token(response.email, response.id)
        user_data_response = user_service.get_user_data(token, response.id)
        return user_data_response

@router.post("/login", response_model=UserDataResponse)
async def login(form_Data: OAuth2PasswordRequestForm = Depends(),
                                 db: Session = Depends(get_db)):
    user_service = UserService(db)
    response = user_service.authenticate(req=UserAuthenticateRequest(email=form_Data.username, password=form_Data.password))
    if not response.user:
        return response
    token = create_access_token(response.user.email, response.user.id)
    user_data_response = user_service.get_user_data(token, response.user.id)
    return user_data_response

# @router.post("/delete_user/{user_id_to_delete}", response_model=GenericResponse)
# async def delete_user(user_id_to_delete: int, user_id: int= Depends(get_current_user),
#                        db: Session = Depends(get_db)):
#     user_service = UserService(db)
#     return user_service.delete(user_id_to_delete, user_id)

