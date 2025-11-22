from typing import List, Dict
from app.repositories.csv_repository import CSVRepository

class BookRepository(CSVRepository):

    def get_books_by_isbn(self, isbn_list: List[str]) -> List[Dict]:
        rows = self.read_all("app/data/Books.csv")
        lookup = {row["ISBN"]: row for row in rows}

        result = []
        for isbn in isbn_list:
            data = lookup.get(isbn)
            if data:
                result.append({
                    "isbn": isbn,
                    "book_title": data.get("Book-Title", "Unknown Title"),
                    "author": data.get("Book-Author", "Unknown Author")
                })
            else:
                result.append({
                    "isbn": isbn,
                    "book_title": "Unknown Title",
                    "author": "Unknown Author"
                })

        return result