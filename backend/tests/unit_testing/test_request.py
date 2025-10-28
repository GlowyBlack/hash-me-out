# import pytest
from backend.app.services.request_service import RequestService
from backend.app.schemas.request import RequestCreate, RequestRead

service = RequestService()

def test_create_request_success():
    
    pass

def test_prevent_duplicate_request():
    pass

def test_generate_request_id_incrementally():
    pass

def test_get_all_requests_returns_list():
    pass

def test_delete_request_reindexes_ids():
    pass


result = RequestRead(
    request_id = 1,
    user_id= 1,
    book_title= "Percy Jackson and the Lightning Thief",
    author = "Rick Riordan",
    isbn= "9780307245304"
)

print(result.book_title)