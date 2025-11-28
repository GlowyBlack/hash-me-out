from pathlib import Path
import csv
from typing import List, Optional

from app.models.book import Book
from app.schemas.book import BookCreate, BookRead, BookUpdate
# from app.repositories.csv_repository import CSVRepository
from app.repositories.books_adapter import BXBooksCSVAdapter


class BookService:
    """
    BookService with:
    - ISBN as primary key (no auto-increment)
    - Admin-only write operations assumed
    - Sharded storage (A.csv, B.csv, ... Z.csv)
    - Safe reads/writes using CSVRepository RWLock
    - Test-friendly (path can be overridden)
    """

    def __init__(self):
        self.repo = BXBooksCSVAdapter()

        # Path = DIR containing shard CSVs
        self.path = (
            Path(__file__).resolve().parents[1] / "data" / "books"
        )

        # Shared CSV structure for all shards
        self.fields = [
            "ISBN",
            "Book-Title",
            "Book-Author",
            "Year-Of-Publication",
            "Publisher",
            "Image-URL-S",
            "Image-URL-M",
            "Image-URL-L",
        ]

    # ---------- SHARD HELPERS ---------- #
    def _determine_shard_from_title(self, title: str) -> str:
        clean = title.strip()
        if not clean:
            return "OTHER"
        first_letter = clean[0].upper()
        return first_letter if first_letter.isalpha() else "OTHER"

    def _find_shard_by_isbn(self, isbn: str) -> Optional[str]:
        """
        Find the shard containing this ISBN by scanning files.
        Only runs when needed; sharding makes it fast.
        """
        if not Path(self.path).exists():
            return None

        for file in Path(self.path).iterdir():
            if file.suffix != ".csv":
                continue
            with open(file, encoding="latin-1") as f:
                reader = csv.DictReader(f, delimiter=";")
                for row in reader:
                    if row["ISBN"] == isbn:
                        return file.stem  # 'A', 'B', ...
        return None

    def _create_shard_if_missing(self, shard: str):
        """Ensure the shard file exists."""
        shard_path = Path(self.path) / f"{shard}.csv"
        shard_path.parent.mkdir(parents=True, exist_ok=True)

        if not shard_path.exists():
            with open(shard_path, "w", encoding="latin-1", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=self.fields, delimiter=";")
                writer.writeheader()

    # ---------- CREATE BOOK ---------- #

    def create_book(self, data: BookCreate) -> BookRead:
        """Insert a new book into its shard. ISBN must be unique."""

        # Check duplicate
        if self.get_book(data.isbn):
            raise ValueError("Book already exists in the database.")

        # Build Book model
        book = Book(
            isbn=data.isbn,
            book_title=data.book_title,
            author=data.author,
            year_of_publication=data.year_of_publication,
            publisher=data.publisher,
            image_url_s=data.image_url_s,
            image_url_m=data.image_url_m,
            image_url_l=data.image_url_l,
        )

        # Determine correct shard
        shard = self._determine_shard_from_title(book.book_title)
        self._create_shard_if_missing(shard)

        shard_path = Path(self.path) / f"{shard}.csv"

        # Append new row (no auto-ID needed)
        self.repo.append_row(shard_path, self.fields, book.to_csv_dict())

        return BookRead(**book.to_api_dict())

    # ---------- GET ALL BOOKS ---------- #

    def get_all_books(self) -> List[BookRead]:
        """Return all books across all shards."""
        results = []
        if not Path(self.path).exists():
            return []

        for file in Path(self.path).iterdir():
            if file.suffix != ".csv":
                continue

            with open(file, encoding="latin-1") as f:
                reader = csv.DictReader(f, delimiter=";")
                for row in reader:
                    book = Book.from_dict(row)
                    results.append(BookRead(**book.to_api_dict()))

        return results

    # ---------- GET ONE BOOK ---------- #

    def get_book(self, isbn: str) -> Optional[BookRead]:
        """Return a single book by ISBN or None."""
        shard = self._find_shard_by_isbn(isbn)
        if not shard:
            return None

        shard_path = Path(self.path) / f"{shard}.csv"
        with open(shard_path, encoding="latin-1") as f:
            reader = csv.DictReader(f, delimiter=";")
            for row in reader:
                if row["ISBN"] == isbn:
                    book = Book.from_dict(row)
                    return BookRead(**book.to_api_dict())
        return None

    # ---------- UPDATE BOOK ---------- #

    def update_book(self, isbn: str, data: BookUpdate) -> Optional[BookRead]:
        """Update book fields; return updated BookRead or None if not found."""
        shard = self._find_shard_by_isbn(isbn)
        if not shard:
            return None

        shard_path = Path(self.path) / f"{shard}.csv"
        rows = self.repo.read_all(shard_path)

        updated = False
        for row in rows:
            if row["ISBN"] == isbn:
                for key, csv_key in [
                    ("book_title", "Book-Title"),
                    ("author", "Book-Author"),
                    ("year_of_publication", "Year-Of-Publication"),
                    ("publisher", "Publisher"),
                    ("image_url_s", "Image-URL-S"),
                    ("image_url_m", "Image-URL-M"),
                    ("image_url_l", "Image-URL-L"),
                ]:
                    value = getattr(data, key)
                    if value is not None:
                        row[csv_key] = value
                updated = True
                break

        if not updated:
            return None

        self.repo.write_all(shard_path, self.fields, rows)
        updated_book = self.get_book(isbn)
        return updated_book

    # ---------- DELETE BOOK ---------- #

    def delete_book(self, isbn: str) -> bool:
        """Delete a book by ISBN. Returns True if deleted, False if not found."""
        shard = self._find_shard_by_isbn(isbn)
        if not shard:
            return False

        shard_path = Path(self.path) / f"{shard}.csv"
        rows = self.repo.read_all(shard_path)

        new_rows = [r for r in rows if r["ISBN"] != isbn]
        if len(new_rows) == len(rows):
            return False  # No deletion happened

        self.repo.write_all(shard_path, self.fields, new_rows)
        return True

    def search_books(self, query: str) -> List[BookRead]:
        """Search across all shards by title, author, or ISBN."""
        results = []
        q = query.lower()

        books_path = Path(self.path)
        if not books_path.exists():
            return []

        for file in books_path.iterdir():
            if file.suffix != ".csv":
                continue

            with open(file, encoding="latin-1") as f:
                reader = csv.DictReader(f, delimiter=";")
                for row in reader:
                    title = row["Book-Title"].lower()
                    author = row["Book-Author"].lower()
                    isbn = row["ISBN"]

                    if q in title or q in author or q in isbn:
                        book = Book.from_dict(row)
                        results.append(BookRead(**book.to_api_dict()))

        return results
    
    def live_search(self, query: str, limit: int = 10) -> List[BookRead]:
        print("SEARCHING IN:", self.path)
        q = query.strip().lower()
        if not q:
            return []

        results = []

        books_dir = Path(self.path)
        if not books_dir.exists():
            return []

        is_isbn_query = q.isdigit()  # user typed only numbers

        for file in books_dir.iterdir():
            if file.suffix != ".csv":
                continue

            with open(file, encoding="latin-1") as f:
                reader = csv.DictReader(f, delimiter=";")

                for row in reader:
                    title = row["Book-Title"].lower()
                    author = row["Book-Author"].lower()
                    isbn = row["ISBN"]

                    # -------------------------
                    # 1. ISBN search (fastest)
                    # -------------------------
                    if is_isbn_query and isbn.startswith(q):
                        book = Book.from_dict(row)
                        results.append(BookRead(**book.to_api_dict()))
                        if len(results) >= limit:
                            return results
                        continue

                    # -------------------------
                    # 2. Prefix match (title/author)
                    # -------------------------
                    if title.startswith(q) or author.startswith(q):
                        book = Book.from_dict(row)
                        results.append(BookRead(**book.to_api_dict()))
                        if len(results) >= limit:
                            return results
                        continue

                    # -------------------------
                    # 3. Substring match fallback
                    # -------------------------
                    if q in title or q in author or q in isbn:
                        book = Book.from_dict(row)
                        results.append(BookRead(**book.to_api_dict()))
                        if len(results) >= limit:
                            return results

        return results

