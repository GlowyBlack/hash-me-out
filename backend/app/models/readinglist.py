from typing import List
from book import Book

class ReadingList:
    def __init__(self, name: str, owner_id: int, is_public: bool = False):
        self.name = name
        self.owner_id = owner_id
        self.is_public = is_public
        self.books: List[Book] = []

    def add_book(self, book: Book):
        if book not in self.books:
            self.books.append(book)

    def remove_book(self, book: Book):
        if book in self.books:
            self.books.remove(book)
