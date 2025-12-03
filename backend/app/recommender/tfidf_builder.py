from sklearn.feature_extraction.text import TfidfVectorizer

class BookVectorizer:
    def __init__(self):
        self.vectorizer = None
        self.book_vectors = None
        self.isbn_to_index = {}
        self.index_to_isbn = {}

    def fit(self, df):
        self.vectorizer = TfidfVectorizer(
            stop_words="english",
            max_features=50000
        )

        self.book_vectors = self.vectorizer.fit_transform(df["combined_text"])

        self.isbn_to_index = {isbn: i for i, isbn in enumerate(df["ISBN"])}
        self.index_to_isbn = {i: isbn for i, isbn in enumerate(df["ISBN"])}

        return self

    def get_vector_by_isbn(self, isbn):
        idx = self.isbn_to_index.get(isbn)
        if idx is None:
            return None
        return self.book_vectors[idx]
    
    def get_all_vectors(self):
        return self.book_vectors
    
    def index_of(self, isbn):
        return self.isbn_to_index.get(isbn)


