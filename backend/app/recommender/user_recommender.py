import numpy as np
from sklearn.preprocessing import normalize
from app.logger import logger
from app.utils.cache import user_vector_cache


from app.recommender.vectorizer_loader import GlobalVectorizer
from app.recommender.interaction_weights import (
    rating_to_weight,
    BASE_INTERACTION_WEIGHTS,
)

class UserProfileRecommender:

    def __init__(self, interaction_service, book_repo):
        """
        interaction_service: UserInteractionService instance
        """
        self.interaction_service = interaction_service
        self.book_repo = book_repo
        self.vectorizer = GlobalVectorizer.get()
        logger.info("UserProfileRecommender initialized.")


    def build_user_vector(self, user_id: int):
        """
        Builds the final user preference vector using positive & negative weights.
        """
        
        cached = user_vector_cache.get(user_id)
        if cached is not None:
            logger.info(f"CACHE HIT     | user_id = {user_id}")
            return cached

        logger.info(f"CACHE MISS    | user_id = {user_id}")
        
        interactions = self.interaction_service.get_user_interactions(user_id)

        if not interactions:
            logger.info(f"NO INTERACTIONS | user_id = {user_id}")
            return None  

        logger.info(f"Building user vector for user {user_id} with {len(interactions)} interactions")
        
        tfidf_matrix = self.vectorizer.book_vectors
        isbn_to_index = self.vectorizer.isbn_to_index

        # Accumulator for user vector
        user_vec = np.zeros(tfidf_matrix.shape[1], dtype=np.float64)
        total_weight_magnitude = 0
        skipped = 0

        for inter in interactions:
            isbn = inter["isbn"]
            inter_type = inter["type"]

            # ----- determine weight -----
            if inter_type == "rating":
                weight = rating_to_weight(inter.get("rating_value"))
            else:
                weight = BASE_INTERACTION_WEIGHTS.get(inter_type, 0)

            if weight == 0:
                continue  # neutral rating or unknown

            # ----- get book vector -----
            book_index = isbn_to_index.get(isbn)
            if book_index is None:
                skipped += 1
                continue
            

            book_vec = tfidf_matrix[book_index].toarray().flatten()

            # ----- apply weight -----
            user_vec += weight * book_vec
            total_weight_magnitude += abs(weight)
        
        logger.info(
            f"VEC BUILT     | user_id = {user_id} skipped = {skipped} weight_mag = {total_weight_magnitude}"
        )

        if total_weight_magnitude == 0:
            logger.warning(f"ZERO WEIGHT   | user_id = {user_id}")
            return None  

        user_vec = normalize(user_vec.reshape(1, -1))[0]
        user_vector_cache.set(user_id, user_vec)
        logger.info(f"CACHE STORE   | user_id = {user_id}")

        return user_vec
