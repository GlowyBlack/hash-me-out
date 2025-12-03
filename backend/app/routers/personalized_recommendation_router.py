from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from app.deps import get_current_user
from app.utils.normalize import normalize_text

from app.recommender.user_recommender import UserProfileRecommender
from app.recommender.similarity_engine import SimilarityEngine

from app.services.user_interaction_service import UserInteractionService
from app.repositories.book_repository import BookRepository
from app.logger import logger

engine = None

router = APIRouter(
    prefix = "/personalized",
    tags = ["Personalized Recommendations"],
)

interaction_service = UserInteractionService()
book_repo = BookRepository()

def get_user_recommender():
    return UserProfileRecommender(interaction_service, book_repo)

def get_engine():
    global engine
    if engine is None:
        engine = SimilarityEngine()
    return engine


@router.get("/")
def personalized_recommendations(
    top_k: int = 10,
    curr = Depends(get_current_user)
):
    """
    Returns personalized recommendations for the current user.
    """
    start = datetime.now()
    user_id = curr["id"]
    logger.info(
        f"API CALL      | /personalized | user_id = {user_id} top_k = {top_k}"
    )

    recommender = get_user_recommender()
    user_vec = recommender.build_user_vector(user_id)

    if user_vec is None:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = "Not enough user interactions to generate personalized recommendations."
        )

    # Step 2 — Collect ISBNs user already interacted with
    interactions = interaction_service.get_user_interactions(user_id)
    interacted_isbns = {inter["isbn"] for inter in interactions}
    interacted_books = {
        ( normalize_text(book["Book-Title"]), normalize_text(book["Book-Author"]) )
        for book in (book_repo.get_book_by_isbn(isbn) for isbn in interacted_isbns)
        if book is not None
    }

    # Step 3 — Run personalized similarity engine
    eng = get_engine()
    recs = eng.recommend_for_user(
        user_vector=user_vec,
        interacted_isbns=interacted_isbns,
        top_k=top_k
    )
    
    results = []
    added_books = set()   
    for rec in recs:
        isbn = rec["isbn"]
        book = book_repo.get_book_by_isbn(isbn)

        if not book:
            continue
        
        title_author = (
            normalize_text(book["Book-Title"]),
            normalize_text(book["Book-Author"])
        )
        if title_author in interacted_books:
            continue

        added_books.add(
            title_author
        )
        results.append({
            "isbn": book["ISBN"],
            "title": book["Book-Title"],
            "author": book["Book-Author"],
            "publisher": book.get("Publisher"),
            "year": book.get("Year-Of-Publication"),
            "image_url_s": book.get("Image-URL-S"),
            "image_url_m": book.get("Image-URL-M"),
            "image_url_l": book.get("Image-URL-L"),
            "score": rec["score"]
        })
        if len(results) >= top_k:
            break
    end = datetime.now()
    duration_ms = (end - start).total_seconds() * 1000
    logger.info(
        f"API DONE      | /personalized | user_id = {user_id} "
        f"returned = {len(results)} took = {duration_ms:.2f}ms"
    )
    return results
