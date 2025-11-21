import pytest
import csv
from unittest import mock
from pydantic import ValidationError
from app.services.readinglist_service import ReadingListService
from app.schemas.readinglist import ReadingListDetail, ReadingListCreate, ReadingListSummary

service = ReadingListService()

@pytest.fixture(autouse=True)
def clean_readinglist_csv(tmp_path):

    service.path = tmp_path / "ReadingLists.csv"

    with open(service.path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=service.fields
        )
        writer.writeheader()

    yield

def test_readinglistcreate_invalid_name_empty():
    with pytest.raises(ValidationError) as exc_info:
        ReadingListCreate(name=" ")
    assert "Readinglist Name must be at least 1 letter" in str(exc_info.value)

def test_create_list_success():
    data = ReadingListCreate(name="My List")

    result = service.create_list(user_id=1, data=data)

    assert isinstance(result, ReadingListDetail)
    assert result.name == "My List"
    assert result.user_id == 1
    assert result.list_id == 1
    assert result.books == []
    assert result.is_public is False

def test_create_list_duplicate_name():
    service.create_list(user_id=1, data=ReadingListCreate(name="List A"))

    with pytest.raises(ValueError) as e:
        service.create_list(user_id=1, data=ReadingListCreate(name="List A"))
    assert "already exists." in str(e.value)  
    
def test_create_list_user_limit():
    for i in range(10):
        service.create_list(user_id=1, data=ReadingListCreate(name=f"L{i}"))

    with pytest.raises(ValueError) as e:
        service.create_list(user_id=1, data=ReadingListCreate(name="Overflow"))
    assert "You can only have 10 reading lists" in str(e.value)

def test_delete_list_success():
    r1 = service.create_list(user_id=1, data=ReadingListCreate(name="A"))
    r2 = service.create_list(user_id=1, data=ReadingListCreate(name="B"))

    ok = service.delete_list(r2.list_id, 1)
    assert ok is True

    all_lists = service.get_all_readinglist(1)
    assert len(all_lists) == 1
    assert all_lists[0].name == "A"

def test_delete_list_not_found():
    ok = service.delete_list(999, 1)
    assert ok is False

def test_rename_success():
    r = service.create_list(1, ReadingListCreate(name="Old Name"))

    ok = service.rename(r.list_id, 1, "New Name")
    assert ok is True

    detail = service.get_list_detail(r.list_id, 1)
    assert detail.name == "New Name"

def test_rename_conflict():
    service.create_list(1, ReadingListCreate(name="List A"))
    r2 = service.create_list(1, ReadingListCreate(name="List B"))

    with pytest.raises(ValueError):
        service.rename(r2.list_id, 1, "List A")

def test_rename_not_found():
    ok = service.rename(999, 1, "New Name")
    assert ok is False

