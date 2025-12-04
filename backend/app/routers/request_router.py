from fastapi import APIRouter, Depends, HTTPException, status
from typing import Literal

from app.schemas.request import RequestCreate
from app.schemas.book import BookCreate
from app.services.request_service import RequestService
from app.services.book_service import BookService
from app.deps import get_current_user

router = APIRouter(prefix="/requests", tags=["Requests"])

service = RequestService()
book_service = BookService()


@router.post(
    "/",
    summary="Create a new book request",
    description="Creates a request for a book and returns the request details.",
    response_description="The newly created Request entry",
)
def create_request(request: RequestCreate, curr=Depends(get_current_user)):
    try:
        return service.create_request(
            user_id=curr["id"],
            data=request,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get(
    "/",
    summary="Retrieve all book requests (Admin only)",
    description="Returns a list of all book requests in the system.",
)
def get_all_requests(curr=Depends(get_current_user)):
    if not curr.get("is_admin"):
        raise HTTPException(status_code=403, detail="Admin privileges required")
    return service.get_all_requests()


@router.delete(
    "/{request_id}",
    summary="Delete a book request (Admin only)",
    description="Deletes a request by ID. Only admins can perform this action.",
    response_description="A confirmation message",
)
def delete_request(request_id: int, curr=Depends(get_current_user)):
    if not curr.get("is_admin"):
        raise HTTPException(status_code=403, detail="Admin privileges required")

    if not service.delete_request(request_id):
        raise HTTPException(
            status_code=404,
            detail="Request not found",
        )

    return {"message": "Request deleted successfully"}


@router.get(
    "/stats",
    summary="Get request statistics (Admin only)",
    description="Returns a list of ISBNs sorted by total request count.",
)
def get_request_stats(
    order: Literal["asc", "desc"] = "desc",
    user=Depends(get_current_user),
):
    if not user["is_admin"]:
        raise HTTPException(status_code=403, detail="Admin privileges required")

    return service.get_total_requested_sorted(order)


@router.post(
    "/{request_id}/accept",
    summary="Accept request and create book",
    description="Admin-only: create a book from a request and delete the request",
)
def accept_request(request_id: int, curr=Depends(get_current_user)):
    if not curr.get("is_admin"):
        raise HTTPException(status_code=403, detail="Admin privileges required")

    req = service.get_request_by_id(request_id)
    if not req:
        raise HTTPException(status_code=404, detail="Request not found")

    title = req.get("title") or req.get("book_title")
    if not title:
        raise HTTPException(
            status_code=500,
            detail="Request is missing a title/book_title field.",
        )

    book_data = BookCreate(
        isbn=req["isbn"],
        book_title=title,
        author=req["author"],
        year_of_publication=None,
        publisher=None,
        image_url_s=None,
        image_url_m=None,
        image_url_l=None,
    )

    try:
        book = book_service.create_book(book_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    service.delete_request(request_id)

    return book
