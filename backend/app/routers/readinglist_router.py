from fastapi import APIRouter, Response, Depends, HTTPException, status
from app.schemas.readinglist import ReadingListCreate, ReadingListRename
from app.services.readinglist_service import ReadingListService
from app.repositories.csv_repository import CSVRepository
from app.repositories.book_repository import BookRepository
from app.deps import get_current_user

router = APIRouter(prefix="/readinglist", tags=["ReadingList"])

service = ReadingListService(repo=CSVRepository(), book_repo=BookRepository())


@router.post(
    "/",
    summary="Create a new reading list",
    description="Creates a reading list owned by the authenticated user.",
    response_description="The newly created reading list.",
)
def create_list(list: ReadingListCreate, curr=Depends(get_current_user)):
    """Creates a new reading list for a user."""
    user_id = curr["id"]
    try:
        return service.create_list(user_id=user_id, data=list)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.delete(
    "/{list_id}",
    summary="Delete a reading list",
    description="Deletes a reading list owned by the authenticated user.",
    response_description="Success message upon deletion.",
)
def delete_list(list_id: int, curr=Depends(get_current_user)):
    """Delete a specific reading list by ID."""
    user_id = curr["id"]
    if not service.delete_list(list_id=list_id, user_id=user_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="ReadingList not found",
        )
    return {"message": "ReadingList deleted successfully"}


@router.put(
    "/{list_id}",
    summary="Rename a reading list",
    description="Renames a reading list owned by the authenticated user.",
    response_description="Success message upon renaming.",
)
def rename_readinglist(
    list_id: int,
    data: ReadingListRename,
    curr=Depends(get_current_user),
):
    """Renames an existing reading list."""
    user_id = curr["id"]
    try:
        if not service.rename(
            list_id=list_id,
            user_id=user_id,
            new_name=data.new_name,
        ):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="ReadingList not found",
            )
        return {"message": "ReadingList renamed successfully"}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.put(
    "/{list_id}/visibility",
    summary="Toggle reading list visibility",
    description="Toggles a reading list between public and private. Only the owner may update visibility.",
    response_description="Updated visibility status.",
)
def toggle_visibility(list_id: int, curr=Depends(get_current_user)):
    """Toggles a reading list's public/private visibility."""
    user_id = curr["id"]
    result = service.toggle_visibility(list_id=list_id, user_id=user_id)
    if result is False:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="ReadingList not found",
        )
    return result


@router.post(
    "/{list_id}/books/{isbn}",
    summary="Add a book to a reading list",
    description="Adds a specific book to the authenticated user's reading list.",
    response_description="Success message when the book is added.",
)
def add_book_to_readinglist(
    list_id: int,
    isbn: str,
    curr=Depends(get_current_user),
):
    """Adds a book to a reading list."""
    user_id = curr["id"]
    try:
        result = service.add_book(list_id=list_id, user_id=user_id, isbn=isbn)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="ReadingList not found",
            )
        return {"message": "Book added successfully"}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.delete(
    "/{list_id}/books/{isbn}",
    summary="Remove a book from a reading list",
    description="Removes a specific book from the authenticated user's reading list.",
    response_description="Success message when the book is removed.",
)
def remove_book_from_readinglist(
    list_id: int,
    isbn: str,
    curr=Depends(get_current_user),
):
    """Removes a book from a reading list."""
    user_id = curr["id"]
    try:
        result = service.remove_book(list_id=list_id, user_id=user_id, isbn=isbn)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="ReadingList not found",
            )
        return {"message": "Book removed successfully"}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get(
    "/public/{user_id}",
    summary="Get a user's public reading lists",
    description="Returns all publicly visible reading lists for the given user.",
)
def get_user_public(user_id: int):
    """Returns all public reading lists for a user."""
    return service.get_user_public_readinglists(user_id=user_id)


@router.get(
    "/{list_id}",
    summary="Get reading list details",
    description="Returns detailed information for a reading list that belongs to the authenticated user.",
)
def get_readinglist_detail(list_id: int, user_id: int):
    """Returns detailed information about a reading list."""
    detail = service.get_list_detail(list_id=list_id, user_id=user_id)
    if not detail:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="ReadingList not found",
        )
    return detail


@router.get(
    "/{list_id}/download",
    summary="Download a reading list as CSV",
    description="Allows the authenticated user to download their reading list as a CSV file.",
    response_class=Response,
)
def download_reading_list(list_id: int, curr=Depends(get_current_user)):
    user_id = curr["id"]

    csv_data, filename = service.export_reading_list_csv(
        list_id=list_id,
        user_id=user_id,
    )

    if not csv_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="ReadingList not found",
        )

    return Response(
        content=csv_data,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )

@router.get(
    "/",
    summary="Get all reading lists for current user",
    description="Returns all reading lists that belong to the authenticated user.",
    response_description="List of reading lists.",
)
def get_my_readinglists(curr=Depends(get_current_user)):
    """Returns all reading lists for the logged in user."""
    user_id = curr["id"]
    return service.get_all_readinglist(user_id=user_id)
