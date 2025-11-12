class Book:
    def __init__(self, isbn: str, book_title: str, author: str, year_of_publication: str | None = None, publisher: str | None = None, image_url_s: str | None = None, image_url_m: str | None = None, image_url_l: str | None = None):
        self.isbn = isbn
        self.book_title = book_title
        self.author = author
        self.year_of_publication = year_of_publication
        self.publisher = publisher
        self.image_url_s = image_url_s
        self.image_url_m = image_url_m
        self.image_url_l = image_url_l

    def to_api_dict(self) -> dict:
        return {
            "isbn": self.isbn,
            "book_title": self.book_title,
            "author": self.author,
            "year_of_publication": self.year_of_publication,
            "publisher": self.publisher,
            "image_url_s": self.image_url_s,
            "image_url_m": self.image_url_m,
            "image_url_l": self.image_url_l,
        }
        
    def to_csv_dict(self) -> dict:
        return {
            "ISBN": self.isbn,
            "Book-Title": self.book_title,
            "Book-Author": self.author,
            "Year-Of-Publication": self.year_of_publication or "",
            "Publisher": self.publisher or "",
            "Image-URL-S": self.image_url_s or "",
            "Image-URL-M": self.image_url_m or "",
            "Image-URL-L": self.image_url_l or "",
        }

    @classmethod
    def from_dict(cls, row: dict):
        return cls(
            isbn=row["ISBN"],
            book_title=row["Book-Title"],
            author=row["Book-Author"],
            year_of_publication=row.get("Year-Of-Publication"),
            publisher=row.get("Publisher"),
            image_url_s=row.get("Image-URL-S"),
            image_url_m=row.get("Image-URL-M"),
            image_url_l=row.get("Image-URL-L"),
        )

    def matches_isbn(self, isbn: str) -> bool:
        return self.isbn == isbn
