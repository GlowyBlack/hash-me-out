from fastapi import APIRouter, Depends, HTTPException, status
from datetime import datetime

from app.deps import get_current_user
from app.logger import logger

from app.recommender.similarity_engine import SimilarityEngine
from app.recommender.user_recommender import UserProfileRecommender
from app.repositories.book_repository import BookRepository
from app.services.user_interaction_service import UserInteractionService
from app.utils.book_identity import normalize_text

engine = None

router = APIRouter(
    prefix="/hybrid",
    tags=["Hybrid Recommendations"]
)

book_repo = BookRepository()
interaction_service = UserInteractionService()

def get_user_recommender():
    return UserProfileRecommender(interaction_service, book_repo)

def get_engine():
    global engine
    if engine is None:
        engine = SimilarityEngine()
    return engine


@router.get("/{isbn}")
def hybrid_recommendations(
    isbn: str,
    top_k: int = 10,
    curr = Depends(get_current_user)
):
    start = datetime.now()
    user_id = curr["id"]

    logger.info(f"[API] /hybrid/{isbn} called by user = {user_id}")

    recommender = get_user_recommender()
    user_vec = recommender.build_user_vector(user_id)
    eng = get_engine()
    
    interactions = interaction_service.get_user_interactions(user_id)

    interacted_isbns = {inter["isbn"] for inter in interactions}

    interacted_books = {
        (
            normalize_text(book["Book-Title"]),
            normalize_text(book["Book-Author"])
        )
        for book in (book_repo.get_book_by_isbn(isbn) for isbn in interacted_isbns)
        if book is not None
    }
    recs = eng.recommend_hybrid(isbn, user_vec, top_k)

    results = []
    added = set()

    for rec in recs:
        r_isbn = rec["isbn"]
        if r_isbn in interacted_isbns:
            continue
        book = book_repo.get_book_by_isbn(rec["isbn"])
        if not book:
            continue

        key = (
            normalize_text(book["Book-Title"]),
            normalize_text(book["Book-Author"])
        )
        if key in added or key in interacted_books:
            continue
        added.add(key)

        results.append({
            "isbn": book["ISBN"],
            "title": book["Book-Title"],
            "author": book["Book-Author"],
            "publisher": book.get("Publisher"),
            "year": book.get("Year-Of-Publication"),
            "image_url_s": book.get("Image-URL-S"),
            "image_url_m": book.get("Image-URL-M"),
            "image_url_l": book.get("Image-URL-L"),
            "hybrid_score": rec["hybrid_score"]
        })

        if len(results) >= top_k:
            break

    elapsed = (datetime.now() - start).total_seconds() * 1000
    logger.info(f"[API] /hybrid/{isbn} done in {elapsed:.2f}ms")

    return results
