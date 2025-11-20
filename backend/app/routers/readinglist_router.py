from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas.readinglist import ReadingListCreate, ReadingListRename
from app.services.readinglist_service import ReadingListService

router = APIRouter(prefix="/readinglist", tags=["ReadingList"])

service = ReadingListService()

@router.post("/")
def create_list(
    list: ReadingListCreate, user_id: int):
    try:
        return service.create_list(user_id=user_id,data=list)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.delete("/{list_id}")
def delete_request( list_id: int, user_id: int):
    """Delete a specific request by ID."""
    if not service.delete_list(list_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="ReadingList not found")
    return {"message": "ReadingList deleted successfully"}

@router.put("/{list_id}")
def rename_readinglist(
    list_id: int, 
    user_id: int, 
    data: ReadingListRename,
):
    try:
        if not service.rename(list_id=list_id, user_id=user_id, new_name=data.new_name):
            raise HTTPException(status_code=404, detail="ReadingList not found")
        return {"message": "ReadingList renamed successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
