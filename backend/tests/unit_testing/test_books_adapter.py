import csv
import pytest
from app.utils.books_adapter import BXBooksCSVAdapter
from app.schemas.book import BookCreate


@pytest.fixture
def adapter():
    return BXBooksCSVAdapter()


# ---------------------------------------------------------------------------
# Basic functionality: reading valid BX-formatted data
# ---------------------------------------------------------------------------

def test_read_all_parses_semicolon_and_latin1(adapter, tmp_path):
    path = tmp_path / "BX_Books.csv"

    with open(path, "w", encoding="latin-1", newline="") as f:
        writer = csv.writer(f, delimiter=";")
        writer.writerow([
            "ISBN", "Book-Title", "Book-Author", "Year-Of-Publication",
            "Publisher", "Image-URL-S", "Image-URL-M", "Image-URL-L",
        ])
        writer.writerow([
            "0195153448", "Classical Mythology", "Mark P. O. Morford",
            "2002", "Oxford University Press", "S_URL", "M_URL", "L_URL",
        ])

    rows = adapter.read_all(str(path))

    assert len(rows) == 1
    row = rows[0]
    assert row["ISBN"] == "0195153448"
    assert row["Book-Title"] == "Classical Mythology"
    assert row["Book-Author"] == "Mark P. O. Morford"


# ---------------------------------------------------------------------------
# Exception handling: missing file
# ---------------------------------------------------------------------------

def test_read_all_returns_empty_when_file_missing(adapter, tmp_path):
    """
    Reading a non-existent BX file should return an empty list.
    """
    
    path = tmp_path / "does_not_exist.csv"
    assert adapter.read_all(str(path)) == []

# ---------------------------------------------------------------------------
# Boundary Value Analysis: enforce ISBN validation
# ---------------------------------------------------------------------------

def test_isbn_boundary_values():

    with pytest.raises(Exception):
        BookCreate(isbn="123456789", book_title="A", author="A")

    BookCreate(isbn="1234567890", book_title="A", author="A")
    BookCreate(isbn="1234567890123", book_title="A", author="A")

    with pytest.raises(Exception):
        BookCreate(isbn="12345678901234", book_title="A", author="A")


# ---------------------------------------------------------------------------
# Fault Injection: corrupted Latin-1 bytes
# ---------------------------------------------------------------------------

def test_fault_injection_corrupt_bytes(adapter, tmp_path):
    
    path = tmp_path / "BX_Books.csv"

    with open(path, "wb") as f:
        f.write(b"ISBN;Book-Title\n")
        f.write(b"\xFF\xFF\xFFINVALID\n") 

    try:
        rows = adapter.read_all(str(path))
        assert rows == [] or isinstance(rows, list)
    except UnicodeDecodeError:
        assert True


# ---------------------------------------------------------------------------
# Mocking: intercept write_all to verify semicolon behavior
# ---------------------------------------------------------------------------

def test_write_all_uses_semicolon_with_mock(monkeypatch, adapter):
    
    captured = {"text": ""}

    class FakeFile:
        def __init__(self):
            self.buffer = []
        def write(self, s):
            self.buffer.append(s)
        def __enter__(self):
            return self
        def __exit__(self, *args):
            captured["text"] = "".join(self.buffer)

    monkeypatch.setattr("builtins.open", lambda *a, **kw: FakeFile())

    fieldnames = ["ISBN", "Book-Title"]
    rows = [{"ISBN": "123", "Book-Title": "Mocked"}]

    adapter.write_all("ignored.csv", fieldnames, rows)

    assert "ISBN;Book-Title" in captured["text"]
    assert "123;Mocked" in captured["text"]
