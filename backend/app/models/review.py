

from datetime import datetime


class Review:
    def __init__(self, review_id: int, book_title: str, author: str, isbn: str):
        self.review_id = review_id
        self.book_title = book_title
        self.author = author
        self.isbn = isbn
        self.time_stamp = datetime.now()
    
    def submit_review():
        pass
        