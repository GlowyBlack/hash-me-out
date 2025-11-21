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
