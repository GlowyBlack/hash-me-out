from pathlib import Path
import csv
from typing import List, Optional

csv.field_size_limit(100_000_000)

from app.models.book import Book
from app.schemas.book import BookCreate, BookRead, BookUpdate
from app.repositories.books_adapter import BXBooksCSVAdapter

# ---------- HEADER & SHARD VALIDATION ---------- #
VALID_FIELDS = [
    "ISBN",
    "Book-Title",
    "Book-Author",
    "Year-Of-Publication",
    "Publisher",
    "Image-URL-S",
    "Image-URL-M",
    "Image-URL-L",
]

def validate_shard(file_path: Path) -> bool:
    """Ensure CSV header matches expected format."""
    try:
        with open(file_path, encoding="latin-1") as f:
            header = f.readline().strip()

        # Accept either delimiter (semicolon = correct, comma = accidental)
        if header.split(";") == VALID_FIELDS:
            return True
        if header.split(",") == VALID_FIELDS:
            return True

        return False

    except Exception:
        return False


class BookService:
    """
    Production-ready BookService with:
    - Safe search
    - Header/delimiter validation
    - Crash-proof shard scanning
    - Consistent CSV schema
    """

    def __init__(self):
        self.repo = BXBooksCSVAdapter()
        self.path = Path(__file__).resolve().parents[1] / "data" / "books"
        self.fields = VALID_FIELDS


    # ---------- SHARD HELPERS ---------- #
    def _determine_shard_from_title(self, title: str) -> str:
        clean = title.strip()
        if not clean:
            return "OTHER"
        first = clean[0].upper()
        return first if first.isalpha() else "OTHER"


    def _find_shard_by_isbn(self, isbn: str) -> Optional[str]:
        books_dir = Path(self.path)
        if not books_dir.exists():
            return None

        for file in books_dir.iterdir():
            if file.suffix != ".csv":
                continue

            with open(file, encoding="latin-1") as f:
                f.seek(0)
                reader = csv.DictReader(f, delimiter=";")

                for row in reader:
                    if row.get("ISBN") == isbn:
                        return file.stem

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
        if self.get_book(data.isbn):
            raise ValueError("Book already exists")

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

        shard = self._determine_shard_from_title(book.book_title)
        self._create_shard_if_missing(shard)

        shard_path = Path(self.path) / f"{shard}.csv"
        self.repo.append_row(shard_path, self.fields, book.to_csv_dict())

        return BookRead(**book.to_api_dict())

    # ---------- GET ALL BOOKS ---------- #

    def get_all_books(self) -> List[BookRead]:
        """Return all books across all shards."""
        results = []
        books_dir = Path(self.path)
        if not books_dir.exists():
            return []

        for file in books_dir.iterdir():
            if file.suffix != ".csv":
                continue

            if not validate_shard(file):
                print(f"[WARNING] Invalid shard skipped: {file.name}")
                continue

            with open(file, encoding="latin-1") as f:
                f.seek(0)
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
            f.seek(0)
            reader = csv.DictReader(f, delimiter=";")

            for row in reader:
                if row["ISBN"] == isbn:
                    return BookRead(**Book.from_dict(row).to_api_dict())

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
        for r in rows:
            if r["ISBN"] == isbn:
                mapping = {
                    "book_title": "Book-Title",
                    "author": "Book-Author",
                    "year_of_publication": "Year-Of-Publication",
                    "publisher": "Publisher",
                    "image_url_s": "Image-URL-S",
                    "image_url_m": "Image-URL-M",
                    "image_url_l": "Image-URL-L",
                }
                for attr, csv_key in mapping.items():
                    val = getattr(data, attr)
                    if val is not None:
                        r[csv_key] = val
                updated = True
                break

        if not updated:
            return None

        self.repo.write_all(shard_path, self.fields, rows)
        return self.get_book(isbn)


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
            return False

        self.repo.write_all(shard_path, self.fields, new_rows)
        return True


    # ---------- SEARCH (FULL) ---------- #

    def search_books(self, query: str) -> List[BookRead]:
        """Case-insensitive search by title, author, or ISBN."""
        results = []
        q = query.lower()
        is_isbn_search = any(char.isdigit() for char in q)

        seen = set()

        for file in Path(self.path).iterdir():
            if file.suffix != ".csv":
                continue
            if not validate_shard(file):
                continue

            with open(file, encoding="latin-1") as f:
                # f.seek(0)
                reader = csv.DictReader(f, delimiter=";")

                for row in reader:
                    title_raw = row["Book-Title"]
                    author_raw = row["Book-Author"]

                    title = title_raw.lower().strip()
                    author = author_raw.lower().strip()

                    isbn = row["ISBN"]

                    # Decide dedupe key based on query type
                    if is_isbn_search:
                        dedupe_key = isbn            # allow multiple editions
                    else:
                        dedupe_key = (title, author)
                    
                    if dedupe_key in seen:
                        continue         
                               
                    if q in title or q in author or q in isbn:
                        results.append(BookRead(**Book.from_dict(row).to_api_dict()))
                        seen.add(dedupe_key)

        return results
    
    # ---------- LIVE SEARCH (FAST PREFIX) ---------- #

    def live_search(self, query: str, limit: int = 10) -> List[BookRead]:
        q = query.strip().lower()
        if not q:
            return []

        results = []
        is_isbn_query = q.isdigit()

        for file in Path(self.path).iterdir():
            if file.suffix != ".csv":
                continue
            if not validate_shard(file):
                continue

            with open(file, encoding="latin-1") as f:
                f.seek(0)
                reader = csv.DictReader(f, delimiter=";")

                for row in reader:
                    title = row["Book-Title"].lower()
                    author = row["Book-Author"].lower()
                    isbn = row["ISBN"]

                    # 1. Fast ISBN prefix
                    if is_isbn_query and isbn.startswith(q):
                        results.append(BookRead(**Book.from_dict(row).to_api_dict()))
                        if len(results) >= limit:
                            return results
                        continue

                    # 2. Title/Author prefix
                    if title.startswith(q) or author.startswith(q):
                        results.append(BookRead(**Book.from_dict(row).to_api_dict()))
                        if len(results) >= limit:
                            return results
                        continue

                    # 3. Substring fallback
                    if q in title or q in author or q in isbn:
                        results.append(BookRead(**Book.from_dict(row).to_api_dict()))
                        if len(results) >= limit:
                            return results

        return results

