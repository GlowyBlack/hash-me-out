from typing import List
from book import Book
import os
import csv

class ReadingList:
    def __init__(self, list_name: str, list_id: int, owner_id: int, is_public: bool = False):
        self.list_name = list_name
        self.list_id = list_id
        self.owner_id = owner_id
        self.is_public = is_public
        self.books: List[Book] = []

    def add_book(self, book: Book):
        if book not in self.books:
            self.books.append(book)

    def remove_book(self, book: Book):
        if book in self.books:
            self.books.remove(book)

    def file_has_header(self, filename:str, header:str) -> bool:
        if not os.path.exists(filename):
            return False
        with open(filename, 'r', encoding='utf-8') as file:
            first_line = file.readline().strip()
            return first_line == header
        
    def __update_reading_list(self):
        file_path = "backend/app/data/Reading_List.csv"
        fieldnames = ['ISBN', 'Total Requested']
        expected_header = ",".join(fieldnames)
        has_header = self.file_has_header(file_path, expected_header)
        all_requests = []
    
    def load_books(filename="BX_Books.csv"):
        books = {}
        with open(filename, newline = '') as f:
            pass
    def __update_request_total(self):
        file_path = "backend/app/data/Total_Requested.csv"
        fieldnames = ['ISBN', 'Total Requested']
        expected_header = ",".join(fieldnames)
        has_header = self.file_has_header(file_path, expected_header)
        all_requests = []