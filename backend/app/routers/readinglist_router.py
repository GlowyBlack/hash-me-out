from fastapi import APIRouter, HTTPException, status
from app.schemas.readinglist import ReadingListCreate
from app.services.readinglist_service import ReadingListService


router = APIRouter(prefix="/readinglist", tags=["ReadingList"])
service = ReadingListService()

@router.post("/")
def create_list(
    request: ReadingListCreate, user_id: int):
    try:
        return service.create_list(user_id,request)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    
