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

    ok = service.delete_list(list_id=r2.list_id, user_id=1)
    assert ok is True

    all_lists = service.get_all_readinglist(user_id=1)
    assert len(all_lists) == 1
    assert all_lists[0].name == "A"

def test_delete_list_not_found():
    ok = service.delete_list(list_id=999, user_id=1)
    assert ok is False

def test_rename_success():
    r = service.create_list(user_id=1, data=ReadingListCreate(name="Old Name"))

    ok = service.rename(list_id=r.list_id, user_id=1, new_name="New Name")
    assert ok is True

    detail = service.get_list_detail(r.list_id, 1)
    assert detail.name == "New Name"

def test_rename_conflict():
    service.create_list(user_id=1, data=ReadingListCreate(name="List A"))
    r2 = service.create_list(user_id=1, data=ReadingListCreate(name="List B"))

    with pytest.raises(ValueError):
        service.rename(list_id=r2.list_id, user_id=1, new_name="List A")

def test_rename_list_not_found():
    ok = service.rename(list_id=999, user_id=1, new_name="New Name")
    assert ok is False

def test_toggle_visibility():
    r = service.create_list(user_id=1, data=ReadingListCreate(name="VisTest"))

    res1 = service.toggle_visibility(list_id=r.list_id, user_id=1)
    assert res1["is_public"] is True

    detail = service.get_list_detail(list_id=r.list_id, user_id=1)
    assert detail.is_public is True

    res2 = service.toggle_visibility(list_id=r.list_id, user_id=1)
    assert res2["is_public"] is False

    detail = service.get_list_detail(list_id=r.list_id, user_id=1)
    assert detail.is_public is False

def test_add_book_success():
    r = service.create_list(user_id=1, data=ReadingListCreate(name="Books"))

    ok = service.add_book(list_id=r.list_id, user_id=1, isbn="9780307245304")
    assert ok is True

    detail = service.get_list_detail(list_id=r.list_id, user_id=1)
    assert len(detail.books) == 1
    assert detail.books[0].isbn == "9780307245304"

def test_add_book_duplicate():
    r = service.create_list(user_id=1, data=ReadingListCreate(name="Books"))
    service.add_book(list_id=r.list_id, user_id=1, isbn="9780307245304")

    with pytest.raises(ValueError):
        service.add_book(list_id=r.list_id, user_id=1, isbn="9780307245304")

def test_remove_book_success():
    r = service.create_list(user_id=1, data=ReadingListCreate(name="Books"))
    service.add_book(list_id=r.list_id, user_id=1, isbn="9780307245304")

    ok = service.remove_book(list_id=r.list_id, user_id=1, isbn="9780307245304")
    assert ok is True

    detail = service.get_list_detail(list_id=r.list_id, user_id=1)
    assert len(detail.books) == 0

def test_remove_book_not_in_list():
    r = service.create_list(user_id=1, data=ReadingListCreate(name="Books"))

    with pytest.raises(ValueError):
        service.remove_book(list_id=r.list_id, user_id=1, isbn="9780307245304")

def test_get_user_public_readinglists():
    r = service.create_list(user_id=1, data=ReadingListCreate(name="PublicList"))
    service.toggle_visibility(list_id=r.list_id, user_id=1)  

    res = service.get_user_public_readinglists(user_id=1)
    assert len(res) == 1
    assert res[0].name == "PublicList"
    assert res[0].is_public is True

def test_get_user_public_empty():
    res = service.get_user_public_readinglists(user_id=1)
    assert res == {"message": "User has no public reading lists"}
