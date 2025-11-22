from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas.readinglist import ReadingListCreate, ReadingListRename
from app.services.readinglist_service import ReadingListService
from app.repositories.csv_repository import CSVRepository
from app.repositories.book_repository import BookRepository

router = APIRouter(prefix="/readinglist", tags=["ReadingList"])

service = ReadingListService(repo=CSVRepository(), book_repo = BookRepository())

@router.post("/")
def create_list(
    list: ReadingListCreate, user_id: int):
    try:
        return service.create_list(user_id=user_id,data=list)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.delete("/{list_id}")
def delete_list( list_id: int, user_id: int):
    """Delete a specific readinglist by ID."""
    if not service.delete_list(list_id=list_id, user_id=user_id):
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

@router.put("/{list_id}/visibility")
def toggle_visibility(list_id: int, user_id: int):
    result = service.toggle_visibility(list_id=list_id, user_id=user_id)
    if result is False:
        raise HTTPException(status_code=404, detail="ReadingList not found")
    return result

@router.post("/{list_id}/books/{isbn}")
def add_book_to_readinglist(list_id: int, isbn: str, user_id: int):
    try:
        result = service.add_book(list_id=list_id, user_id=user_id, isbn=isbn)
        if not result:
            raise HTTPException(status_code=404, detail="ReadingList not found")
        return {"message": "Book added successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{list_id}/books/{isbn}")
def remove_book_from_readinglist(list_id: int, isbn: str, user_id: int):
    try:
        result = service.remove_book(list_id=list_id, user_id=user_id, isbn=isbn)
        if not result:
            raise HTTPException(status_code=404, detail="ReadingList not found")
        return {"message": "Book removed successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/public/{user_id}")
def get_user_public(user_id: int):
    return service.get_user_public_readinglists(user_id)

@router.get("/{list_id}")
def get_readinglist_detail(list_id: int, user_id: int):
    detail = service.get_list_detail(list_id, user_id)
    if not detail:
        raise HTTPException(404, "ReadingList not found")
    return detail
