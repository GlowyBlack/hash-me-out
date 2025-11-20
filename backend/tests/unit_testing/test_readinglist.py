import pytest
from unittest import mock
from pydantic import ValidationError
from app.services.readinglist_service import ReadingListService
from app.schemas.readinglist import ReadingListDetail, ReadingListCreate

service = ReadingListService()

def test_readinglistcreate_invalid_name_empty():
    with pytest.raises(ValidationError) as exc_info:
        ReadingListCreate(name=" ")
    assert "Readinglist Name must be at least 1 letter" in str(exc_info.value)
    
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
    
@mock.patch("app.services.readinglist_service.CSVRepository.write_all")
@mock.patch("app.services.readinglist_service.CSVRepository.read_all")
def test_delete_readinglist_success(mock_read_all, mock_write_all):
    mock_read_all.return_value = [
        {"ListID": "1", "UserID": "1", "Name": "List A", "Books": "[]"},
        {"ListID": "2", "UserID": "1", "Name": "List B", "Books": "[]"},
        {"ListID": "3", "UserID": "2", "Name": "List A", "Books": "[]"},
    ]

    result = service.delete_list(list_id=2, user_id=1)
    assert result is True

    expected_rows = [
        {"ListID": "1", "UserID": "1", "Name": "List A", "Books": "[]"},
        {"ListID": "2", "UserID": "2", "Name": "List A", "Books": "[]"},
    ]

    mock_write_all.assert_called_once_with(
        service.path,
        service.fields,
        expected_rows
    )

@mock.patch("app.services.readinglist_service.CSVRepository.write_all")
@mock.patch("app.services.readinglist_service.CSVRepository.read_all")
def test_delete_readinglist_failure(mock_read_all, mock_write_all):
    mock_read_all.return_value = [
        {"ListID": "1", "UserID": "1", "Name": "List A", "Books": "[]"},
        {"ListID": "2", "UserID": "1", "Name": "List B", "Books": "[]"},
        {"ListID": "3", "UserID": "2", "Name": "List A", "Books": "[]"},
    ]

    result = service.delete_list(list_id=2, user_id=2)
    assert result is False
    mock_write_all.assert_not_called()

@mock.patch("app.services.readinglist_service.CSVRepository.write_all")
@mock.patch("app.services.readinglist_service.CSVRepository.read_all")
def test_rename_readinglist_success(mock_read_all, mock_write_all):
    mock_read_all.return_value = [
        {"ListID": "1", "UserID": "1", "Name": "List A", "Books": "[]"},
        {"ListID": "2", "UserID": "1", "Name": "List B", "Books": "[]"},
        {"ListID": "3", "UserID": "2", "Name": "List A", "Books": "[]"},
    ]

    result = service.rename(list_id=1, user_id=1, new_name="New Name")
    assert result is True
    mock_write_all.assert_called_once()
    updated_rows = mock_write_all.call_args[0][2]  
    assert updated_rows[0]["Name"] == "New Name"

@mock.patch("app.services.readinglist_service.CSVRepository.write_all")
@mock.patch("app.services.readinglist_service.CSVRepository.read_all")
def test_rename_readinglist_conflict(mock_read_all, mock_write_all):
    mock_read_all.return_value = [
        {"ListID": "1", "UserID": "1", "Name": "Old Name", "Books": "[]"},
        {"ListID": "2", "UserID": "1", "Name": "Another List", "Books": "[]"}
    ]

    with pytest.raises(ValueError) as e:
        service.rename(list_id=1, user_id=1, new_name="Another List")
    assert 'already exists' in str(e.value)
    mock_write_all.assert_not_called()


@mock.patch("app.services.readinglist_service.CSVRepository.write_all")
@mock.patch("app.services.readinglist_service.CSVRepository.read_all")
def test_rename_readinglist_not_found(mock_read_all, mock_write_all):
    mock_read_all.return_value = [
        {"ListID": "1", "UserID": "1", "Name": "List A", "Books": "[]"},
        {"ListID": "2", "UserID": "1", "Name": "List B", "Books": "[]"},
        {"ListID": "3", "UserID": "1", "Name": "List C", "Books": "[]"},
    ]

    result = service.rename(list_id=4, user_id=1, new_name="New Name")
    
    assert result is False
    mock_write_all.assert_not_called()