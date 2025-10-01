from ....schemas.user import UserCreateRequest, UserCreateResponse
from fastapi import APIRouter, Depends
from ....services.user_service import UserService
from ....db.session import get_db
from sqlalchemy.orm import Session

router = APIRouter()

@router.post("/create_user", response_model=UserCreateResponse)
async def create_user(user_create_request: UserCreateRequest, db: Session = Depends(get_db)):
    user_service = UserService(db)
    return user_service.create(user_create_request)