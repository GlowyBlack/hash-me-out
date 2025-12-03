import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from app.recommender.vectorizer_loader import GlobalVectorizer
from app.logger import logger
from app.utils.cache import similarity_cache
from app.utils.book_identity import normalize_text 


class SimilarityEngine:
    def __init__(self):
        self.vectorizer = GlobalVectorizer.get()
        if self.vectorizer is None:
            logger.error("GlobalVectorizer is not loaded! Cannot initialize SimilarityEngine.")
            raise RuntimeError(
                "Vectorizer not loaded. "
                "Call GlobalVectorizer.load() in app/main.py startup event."
            )
        logger.info("SimilarityEngine initialized.")




    def recommend_for_book(self, isbn: str, top_k: int = 10):
        """
        Returns top-k similar books using cosine similarity.
        Uses caching to avoid recomputation.
        """
        cache_key = (isbn, top_k)

        cached = similarity_cache.get(cache_key)
        if cached is not None:
            logger.info(f"CACHE HIT     | isbn = {isbn} top_k = {top_k}")
            return cached

        logger.info(f"CACHE MISS    | isbn = {isbn} top_k = {top_k}")

        idx = self.vectorizer.index_of(isbn)
        if idx is None:
            logger.warning(f"NOT FOUND     | isbn = {isbn}")
            return []

        target_vector = self.vectorizer.get_vector_by_isbn(isbn)
        all_vectors = self.vectorizer.get_all_vectors()

        # Compute cosine similarity
        scores = cosine_similarity(target_vector, all_vectors)[0]

        top_indices = np.argsort(scores)[::-1]
        INTERNAL_LIMIT = max(top_k * 50, 500)

        top_indices = [i for i in top_indices if i != idx][:INTERNAL_LIMIT]

        results =  [
            {
                "isbn": self.vectorizer.index_to_isbn[i],
                "score": float(scores[i])
            }
            for i in top_indices
        ]
        similarity_cache.set(cache_key, results)
        logger.info(f"CACHE STORE   | isbn = {isbn} top_k = {top_k}")

        return results

    def recommend_for_user(self, user_vector: np.ndarray, interacted_isbns=None, top_k: int = 10):
        """
        Personalized recommendation based on a user profile vector.
        """
        logger.info("PERSONALIZED  | computing user-based similarity")
        if user_vector is None:
            return []  # no profile available

        sims = cosine_similarity(
            user_vector.reshape(1, -1),
            self.vectorizer.book_vectors
        )[0]

        ranked_idx = sims.argsort()[::-1]
        INTERNAL_LIMIT = max(top_k * 10, 500)

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
        logger.info(f"RETURNING     | {len(result)} personalized recs")

        return result
    
    def recommend_hybrid(self, isbn: str, user_vector, top_k: int = 10):
        """
        Hybrid = 60% content-based + 40% user-personalized.
        If user_vector is None → fall back to content-only.
        """
        logger.info(f"HYBRID        | begin | isbn={isbn}")

        # ----------- 1. Content-based similarity for this ISBN -----------
        CONTENT_SAMPLE_SIZE = 200  

        content_recs = self.recommend_for_book(isbn, CONTENT_SAMPLE_SIZE)  
        content_scores = {rec["isbn"]: rec["score"] for rec in content_recs}

        if user_vector is None:
            logger.info("HYBRID        | content-only (no user vector)")
            return [
                {"isbn": isbn, "hybrid_score": float(score)}
                for isbn, score in list(content_scores.items())[:top_k]
            ]

        user_sims = cosine_similarity(
            user_vector.reshape(1, -1),
            self.vectorizer.book_vectors
        )[0]

        user_scores = {
            self.vectorizer.index_to_isbn[i]: float(user_sims[i])
            for i in range(len(user_sims))
        }

        HYBRID_ALPHA = 0.6  # content weight
        HYBRID_BETA = 0.4   # user weight

        hybrid_scores = {}

        for isbn_key, c_score in content_scores.items():
            u_score = user_scores.get(isbn_key, 0)
            hybrid = HYBRID_ALPHA*c_score + HYBRID_BETA*u_score
            hybrid_scores[isbn_key] = hybrid

        sorted_isbns = sorted(hybrid_scores, key=lambda x: hybrid_scores[x], reverse=True)
        INTERNAL_LIMIT = max(top_k * 20, 500)

        results =  [
            {
                "isbn": i,
                "hybrid_score": float(hybrid_scores[i]),
            }
            for i in sorted_isbns[:INTERNAL_LIMIT] 
        ]
        
        logger.info(f"HYBRID        | done | isbn={isbn} candidates={len(results)}")
        return results