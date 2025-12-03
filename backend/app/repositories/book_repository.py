from typing import List, Dict
from app.repositories.books_adapter import BXBooksCSVAdapter

class BookRepository(BXBooksCSVAdapter):

    def __init__(self):
        super().__init__()

        rows = self.read_all("app/data/BX_Books.csv")

        self._isbn_map: Dict[str, Dict] = {
            row["ISBN"]: row for row in rows
        }

        self._all_books = rows

        print(f"[BookRepository] Loaded {len(self._isbn_map)} books into memory.")


    def get_books_by_isbn(self, isbn_list: List[str]) -> List[Dict]:
        result = []
        for isbn in isbn_list:
            data = self._isbn_map.get(isbn)
            if data:
                result.append({
                    "isbn": isbn,
                    "book_title": data.get("Book-Title", "Unknown Title"),
                    "author": data.get("Book-Author", "Unknown Author"),
                })
            else:
                result.append({
                    "isbn": isbn,
                    "book_title": "Unknown Title",
                    "author": "Unknown Author",
                })

        return result


    def get_book_by_isbn(self, isbn: str):
        return self._isbn_map.get(isbn)
