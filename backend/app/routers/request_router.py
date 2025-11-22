from fastapi import APIRouter, HTTPException
from app.schemas.request import RequestCreate
from app.services.request_service import RequestService

router = APIRouter(prefix="/requests", tags=["Requests"])
service = RequestService()

@router.post("/")
def create_request(
    request: RequestCreate, user_id: int):
    try:
        return service.create_request(user_id=user_id, data=request)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/")
def get_all_requests():
    """List all book requests."""
    return service.get_all_requests()

@router.delete("/{request_id}")
def delete_request( request_id: int):
    """Delete a specific request by ID."""
    if not service.delete_request(request_id=request_id):
        raise HTTPException(status_code=404, detail="Request not found")
    return {"message": "Request deleted successfully"}
    
    
