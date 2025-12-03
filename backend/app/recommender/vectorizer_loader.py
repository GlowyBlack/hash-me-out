from app.recommender.tfidf_builder import BookVectorizer
from app.recommender.recommender_data import load_enriched_books
import threading


class GlobalVectorizer:
    """Production loads exactly once at startup."""

    _instance = None
    _lock = threading.Lock()

    # LOAD FROM CSV (used in production startup)
    @classmethod
    def load(cls, csv_path: str):
        with cls._lock:
            if cls._instance is None:
                df = load_enriched_books(csv_path)
                cls._instance = BookVectorizer().fit(df)
            return cls._instance

    # LOAD FROM DATAFRAME (used for testing)
    @classmethod
    def load_from_df(cls, df):
        with cls._lock:
            if cls._instance is None:
                cls._instance = BookVectorizer().fit(df)
            return cls._instance

    # GET CURRENT INSTANCE
    @classmethod
    def get(cls):
        return cls._instance

    # RESET FOR TESTING ONLY
    # Clears the global vectorizer so tests can safely reload
    @classmethod
    def reset(cls):
        with cls._lock:
            cls._instance = None

    # HELPER FOR TESTS OR DEBUGGING
    @classmethod
    def is_loaded(cls):
        return cls._instance is not None
