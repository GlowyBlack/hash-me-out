

class Rating:
    def __init__(self, user_id: int, isbn: str, rating: int):
        self.user_id = user_id
        self.isbn = isbn
        self.rating = rating  # 1-5 or 1-10 depending on your system
