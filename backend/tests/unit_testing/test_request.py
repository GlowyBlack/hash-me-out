import csv
import pytest
from app.services.request_service import RequestService
from app.schemas.request import RequestCreate, RequestRead
from pydantic import ValidationError


@pytest.fixture
def service(tmp_path):

    svc = RequestService()

    svc.path = tmp_path / "Requests.csv"
    svc.totalpath = tmp_path / "Total_Requested.csv"

    with open(svc.path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=svc.fields)
        writer.writeheader()

    with open(svc.totalpath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=svc.total_fields)
        writer.writeheader()

    return svc

def test_create_request_fail():
    with pytest.raises(ValidationError) as exc_info:
        RequestCreate(
            book_title = "Percy Jackson and the Lightning Thief",
            author = "Rick Riordan",
            isbn = "123456"
        )

    assert "ISBN must contain exactly 10 or 13 digits" in str(exc_info.value)

def test_create_request_success(service):
    test_data = RequestCreate(
        book_title = "Percy Jackson and the Lightning Thief",
        author = "Rick Riordan",
        isbn = "9780307245304"
    )

    result = service.create_request(1, data=test_data)

    expected = RequestRead(
        request_id = 1,
        user_id = 1,
        book_title = "Percy Jackson and the Lightning Thief",
        author = "Rick Riordan",
        isbn = "9780307245304"
    )

    assert result == expected

def test_prevent_duplicate_request(service):
    req = RequestCreate(
        book_title = "Percy Jackson and the Lightning Thief",
        author = "Rick Riordan",
        isbn = "9780307245304"
    )

    service.create_request(1, data=req)

    with pytest.raises(ValueError, match = "already requested"):
        service.create_request(1, data=req)

