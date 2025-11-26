from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas.request import RequestCreate
from app.services.request_service import RequestService
from app.deps import get_current_user

router = APIRouter(prefix = "/requests", tags = ["Requests"])
service = RequestService()

@router.post("/",
    summary = "Create a new book request",
    description = "Creates a request for a book and returns the request details.",
    response_description="The newly created Request entry"
)
def create_request(request: RequestCreate,
                   curr = Depends(get_current_user)):
    user_id = curr["id"]
    try:
        return service.create_request(user_id = user_id, data = request)
    except ValueError as e:
        raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, detail = str(e))

@router.get(
    "/",
    summary = "Retrieve all book requests",
    description = "Returns a list of all book requests in the system."
)
def get_all_requests(curr = Depends(get_current_user)):
    """List all book requests."""
    if not curr.get("is_admin"):
        raise HTTPException(status_code = status.HTTP_403_FORBIDDEN, detail = "Admin privileges required")
    return service.get_all_requests()

@router.delete(
    "/{request_id}",
    summary = "Delete a book request",
    description = "Deletes a request by ID. Only admins can perform this action.",
    response_description = "A confirmation message on successful deletion.")
def delete_request(request_id: int,
                   curr = Depends(get_current_user)):
    """Delete a specific request by ID."""
    if not curr.get("is_admin"):
        raise HTTPException(status_code=403, detail="Admin privileges required")
    if not service.delete_request(request_id = request_id):
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "Request not found")
    return {"message": "Request deleted successfully"}
    
    
