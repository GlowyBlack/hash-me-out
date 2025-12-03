import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from app.recommender.vectorizer_loader import GlobalVectorizer


class SimilarityEngine:
    def __init__(self):
        self.vectorizer = GlobalVectorizer.get()
        if self.vectorizer is None:
            raise RuntimeError(
                "Vectorizer not loaded. "
                "Call GlobalVectorizer.load() in app/main.py startup event."
            )

    def recommend_for_book(self, isbn: str, top_k: int = 10):
        """
        Returns top-k similar books using cosine similarity.
        """

        idx = self.vectorizer.index_of(isbn)
        if idx is None:
            print(f"[WARN] ISBN {isbn} not found.")
            return []

        target_vector = self.vectorizer.get_vector_by_isbn(isbn)
        all_vectors = self.vectorizer.get_all_vectors()

        # Compute cosine similarity
        scores = cosine_similarity(target_vector, all_vectors)[0]

        # Sort by highest similarity
        top_indices = np.argsort(scores)[::-1]
        top_indices = [i for i in top_indices if i != idx][:top_k]

        return [
            {
                "isbn": self.vectorizer.index_to_isbn[i],
                "score": float(scores[i])
            }
            for i in top_indices
        ]

    def recommend_for_user(self, user_vector: np.ndarray, interacted_isbns=None, top_k: int = 10):
        """
        Personalized recommendation based on a user profile vector.
        """

        if user_vector is None:
            return []  # no profile available

        # Compute cosine similarity for ALL books (fast)
        sims = cosine_similarity(
            user_vector.reshape(1, -1),
            self.vectorizer.book_vectors
        )[0]

        ranked_idx = sims.argsort()[::-1]
        INTERNAL_LIMIT = max(top_k * 10, 100)

        result = []
        for i in ranked_idx[:INTERNAL_LIMIT]:
            isbn = self.vectorizer.index_to_isbn[i]

            if interacted_isbns and isbn in interacted_isbns:
                continue

            result.append({
                "isbn": isbn,
                "score": float(sims[i]),
            })

            # if len(result) == top_k:
            #     break

        return result