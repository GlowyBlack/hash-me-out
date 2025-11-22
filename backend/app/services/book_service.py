from pathlib import Path
from app.models.book import Book
from app.utils.books_adapter import BXBooksCSVAdapter
from app.utils.data_manager import CSVRepository
from app.schemas.book import BookCreate, BookRead, BookUpdate


class BookService:
    def __init__(self):
        self.repo = BXBooksCSVAdapter()
        self.path = str(Path(__file__).resolve().parents[1] / "data" / "BX_Books.csv")
        self.fields = ["ISBN", 
                       "Book-Title",
                       "Book-Author", 
                       "Year-Of-Publication", 
                       "Publisher", 
                       "Image-URL-S", 
                       "Image-URL-M", 
                       "Image-URL-L"
                    ]
        

    def __book_exists(self, isbn: str) -> bool:
        rows = self.repo.read_all(self.path)
        return any(r["ISBN"] == isbn for r in rows)

    def __load_book_or_none(self, isbn: str):
        rows = self.repo.read_all(self.path)
        for row in rows:
            if row["ISBN"] == isbn:
                return row
        return None
    
    def get_all_books(self) -> list[BookRead]:
        rows = self.repo.read_all(self.path)
        return [
            BookRead(**Book.from_dict(r).to_api_dict())
            for r in rows
        ]

    def get_book(self, isbn: str):
        row = self.__load_book_or_none(isbn)
        if not row:
            return None
        return BookRead(**Book.from_dict(row).to_api_dict())

    def create_book(self, data: BookCreate) -> BookRead:
        if self.__book_exists(data.isbn):
            raise ValueError("Book already exists in the database.")

        book = Book(
            isbn = data.isbn,
            book_title = data.book_title,
            author = data.author,
            year_of_publication = data.year_of_publication,
            publisher = data.publisher,
            image_url_s = data.image_url_s,
            image_url_m = data.image_url_m,
            image_url_l = data.image_url_l
        )

        self.repo.append_row(self.path, self.fields, book.to_csv_dict())

        return BookRead(**book.to_api_dict())

    def update_book(self, isbn: str, data: BookUpdate):
        rows = self.repo.read_all(self.path)
        update_data = data.model_dump(exclude_unset = True)

        FIELD_MAP = {
            "book_title": "Book-Title",
            "author": "Book-Author",
            "year_of_publication": "Year-Of-Publication",
            "publisher": "Publisher",
            "image_url_s": "Image-URL-S",
            "image_url_m": "Image-URL-M",
            "image_url_l": "Image-URL-L"
        }

        updated = False
        for r in rows:
            if r["ISBN"] == isbn:
                for key, csv_key in FIELD_MAP.items():
                    if key in update_data:
                        r[csv_key] = update_data[key]
                updated = True
                break

        if not updated:
            return None

        self.repo.write_all(self.path, self.fields, rows)
        row = self.__load_book_or_none(isbn)
        return BookRead(**Book.from_dict(row).to_api_dict())

    def delete_book(self, isbn: str) -> bool:

        rows = self.repo.read_all(self.path)
        new_rows = [r for r in rows if r["ISBN"] != isbn]

        if len(new_rows) == len(rows):
            return False  

        self.repo.write_all(self.path, self.fields, new_rows)
        return True
