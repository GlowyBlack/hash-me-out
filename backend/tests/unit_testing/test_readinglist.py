import pytest
from app.services.readinglist_service import ReadingListService
from app.schemas.readinglist import ReadingListDetail, ReadingListCreate

service = ReadingListService()
def test_create_list_success():
    expected_result = ReadingListDetail(
        user_id=1,
        list_id=1,
        name = "Test Reading List",
        books = []        
    )
    test_data = ReadingListCreate(name = "Test Reading List")
    result = service.create_list(user_id=1, data = test_data)
    assert isinstance(result, ReadingListDetail)
    assert result.name == expected_result.name
    assert result.books == expected_result.books
