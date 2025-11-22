import csv
import pytest
from app.repositories.books_adapter import BXBooksCSVAdapter
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
# Writing: correct delimiter, encoding, and readable output
# ---------------------------------------------------------------------------

def test_write_all_creates_valid_bx_file(adapter, tmp_path):
    """
    write_all should produce semicolon-separated, Latin-1 encoded output.
    """
    path = tmp_path / "BX_Books.csv"

    fieldnames = [
        "ISBN", "Book-Title", "Book-Author", "Year-Of-Publication",
        "Publisher", "Image-URL-S", "Image-URL-M", "Image-URL-L",
    ]

    rows = [{
        "ISBN": "1111111111",
        "Book-Title": "Test Book",
        "Book-Author": "Test Author",
        "Year-Of-Publication": "1999",
        "Publisher": "Test Publisher",
        "Image-URL-S": "",
        "Image-URL-M": "",
        "Image-URL-L": "",
    }]

    adapter.write_all(str(path), fieldnames, rows)

    with open(path, "r", encoding="latin-1") as f:
        content = f.read()

    assert "ISBN;Book-Title" in content
    assert "1111111111;Test Book;Test Author" in content

    parsed = adapter.read_all(str(path))
    assert len(parsed) == 1
    assert parsed[0]["ISBN"] == "1111111111"


# ---------------------------------------------------------------------------
# Appending: ensure new rows do not overwrite previous data
# ---------------------------------------------------------------------------

def test_append_row_appends_without_overwriting(adapter, tmp_path):
    
    path = tmp_path / "BX_Books.csv"

    fieldnames = [
        "ISBN", "Book-Title", "Book-Author", "Year-Of-Publication",
        "Publisher", "Image-URL-S", "Image-URL-M", "Image-URL-L",
    ]

    adapter.write_all(str(path), fieldnames, [{
        "ISBN": "1111111111",
        "Book-Title": "First Book",
        "Book-Author": "First Author",
        "Year-Of-Publication": "2000",
        "Publisher": "P1",
        "Image-URL-S": "",
        "Image-URL-M": "",
        "Image-URL-L": "",
    }])

    adapter.append_row(str(path), fieldnames, {
        "ISBN": "2222222222",
        "Book-Title": "Second Book",
        "Book-Author": "Second Author",
        "Year-Of-Publication": "2001",
        "Publisher": "P2",
        "Image-URL-S": "",
        "Image-URL-M": "",
        "Image-URL-L": "",
    })

    rows = adapter.read_all(str(path))

    assert len(rows) == 2
    assert rows[0]["ISBN"] == "1111111111"
    assert rows[1]["ISBN"] == "2222222222"


# ---------------------------------------------------------------------------
# Equivalence Partitioning: valid, malformed, and empty rows
# ---------------------------------------------------------------------------

def test_read_all_equivalence_partitions(adapter, tmp_path):
    
    path = tmp_path / "BX_Books.csv"

    with open(path, "w", encoding="latin-1") as f:
        f.write("ISBN;Book-Title\n")
        f.write("1111111111;Good Book\n")  
        f.write(";\n")                     
        f.write("\n")                       

    rows = adapter.read_all(str(path))

    assert any(r.get("ISBN") == "1111111111" for r in rows)
