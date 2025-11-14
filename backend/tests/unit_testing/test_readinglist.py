import pytest
from unittest import mock
from pydantic import ValidationError
from app.services.readinglist_service import ReadingListService
from app.schemas.readinglist import ReadingListDetail, ReadingListCreate

service = ReadingListService()
@mock.patch("app.services.readinglist_service.CSVRepository.append_row")
@mock.patch("app.services.readinglist_service.CSVRepository.read_all")
def test_create_list_success(mock_read_all, mock_append_row):
    mock_read_all.return_value = []
    test_data = ReadingListCreate(name="My Test Reading List")

    result = service.create_list(user_id=1, data=test_data)
    expected_result = ReadingListDetail(
        user_id=1,
        list_id=1,
        name="My Test Reading List",
        books=[]
    )
    assert isinstance(result, ReadingListDetail)
    assert result.name == "My Test Reading List"
    assert result.books == expected_result.books
    assert result.user_id == expected_result.user_id
    assert result.list_id == expected_result.list_id
    mock_append_row.assert_called_once()

def test_readinglistcreate_invalid_name_empty():
    with pytest.raises(ValidationError) as exc_info:
        ReadingListCreate(name=" ")
    assert "Readinglist Name must be at least 1 letter" in str(exc_info.value)