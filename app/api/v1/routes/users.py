from ....schemas.user import UserCreateRequest
from ....schemas.generic import GenericResponse
from fastapi import APIRouter, Depends
from ....services.user_service import UserService
from ....db.session import get_db
from sqlalchemy.orm import Session
from ...deps import get_current_user

router = APIRouter()

@router.post("/create_admin", response_model=GenericResponse)
async def create_admin(user_create_request: UserCreateRequest, db: Session = Depends(get_db)):
    user_service = UserService(db)
    return user_service.create_admin(user_create_request)

@router.post("/create_user", response_model=GenericResponse)
async def create_user(user_create_request: UserCreateRequest, db: Session = Depends(get_db)):
    user_service = UserService(db)
    return user_service.create_user(user_create_request)

@router.post("/delete_user/{user_id_to_delete}", response_model=GenericResponse)
async def delete_user(user_id_to_delete: int, user_id: int= Depends(get_current_user),
                       db: Session = Depends(get_db)):
    user_service = UserService(db)
    return user_service.delete(user_id_to_delete, user_id)

