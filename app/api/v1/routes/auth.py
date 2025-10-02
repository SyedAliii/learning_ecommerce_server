from ....schemas.user import UserAuthenticateRequest
from fastapi import APIRouter, Depends
from ....services.user_service import UserService
from ....db.session import get_db
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from ....core.security import create_access_token

router = APIRouter()

@router.post("/login")
async def login_for_access_token(form_Data: OAuth2PasswordRequestForm = Depends(),
                                 db: Session = Depends(get_db)):
    user_service = UserService(db)
    auth_Response = user_service.authenticate(req=UserAuthenticateRequest(email=form_Data.username, password=form_Data.password))
    if not auth_Response.user:
        return auth_Response
    token = create_access_token(auth_Response.user.email, auth_Response.user.id)
    return {"token": token}