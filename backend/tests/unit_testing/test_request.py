import pytest
from app.services.request_service import RequestService
from app.schemas.request import RequestCreate, RequestRead

service = RequestService()

def test_create_request_success():
    expected_result = RequestRead(
                        request_id = 1,
                        user_id= 1,
                        book_title= "Percy Jackson and the Lightning Thief",
                        author = "Rick Riordan",
                        isbn= "9780307245304",
                        time= 2025-10-28)
    
    test_data = RequestCreate(book_title="Percy Jackson and the Lightning Thief", 
                              author = "Rick Riordan", 
                              isbn= "9780307245304")
    result = service.create_request(1, data= test_data)
    assert result == expected_result
    
def test_prevent_duplicate_request():
    duplicate_request = RequestCreate(book_title= "Percy Jackson and the Lightning Thief",
                                      author = "Rick Riordan",
                                      isbn= "9780307245304")
    with pytest.raises(ValueError, match="This user has already requested this book."):
        service.create_request(1, data= duplicate_request)



def test_get_all_requests_returns_list():
    result = service.get_all_requests()
    assert len(result) == 1
    service.delete_request(1)


