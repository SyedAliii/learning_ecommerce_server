from app.schemas.generic import GenericResponse
from app.schemas.search import SearchResponse
from fastapi import APIRouter, Depends
from app.services.search_service import SearchService
from app.db.session import get_db
from sqlalchemy.orm import Session

router = APIRouter()

@router.get("/search", response_model=SearchResponse)
async def search_product(query: str, db: Session = Depends(get_db)):
    search_service = SearchService(db)
    return search_service.search(query)
