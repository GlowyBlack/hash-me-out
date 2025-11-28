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

def test_get_total_requested_sorted_desc(service):
    rows = [
        {"ISBN": "1111111111", "Total Requested": "2"},
        {"ISBN": "2222222222", "Total Requested": "5"},
        {"ISBN": "3333333333", "Total Requested": "1"},
    ]

    with open(service.totalpath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=service.total_fields)
        writer.writeheader()
        writer.writerows(rows)

    result = service.get_total_requested_sorted(order="desc")

    isbns_in_order = [r["ISBN"] for r in result]
    assert isbns_in_order == ["2222222222", "1111111111", "3333333333"]
    assert result[0]["Total Requested"] == 5
    assert result[1]["Total Requested"] == 2
    assert result[2]["Total Requested"] == 1


def test_get_total_requested_sorted_asc(service):
    rows = [
        {"ISBN": "1111111111", "Total Requested": "2"},
        {"ISBN": "2222222222", "Total Requested": "5"},
        {"ISBN": "3333333333", "Total Requested": "1"},
    ]

    with open(service.totalpath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=service.total_fields)
        writer.writeheader()
        writer.writerows(rows)

    result = service.get_total_requested_sorted(order="asc")

    isbns_in_order = [r["ISBN"] for r in result]
    assert isbns_in_order == ["3333333333", "1111111111", "2222222222"]
    assert result[0]["Total Requested"] == 1
    assert result[1]["Total Requested"] == 2
    assert result[2]["Total Requested"] == 5
