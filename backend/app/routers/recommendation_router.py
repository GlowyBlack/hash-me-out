from fastapi import APIRouter, HTTPException, status
from app.recommender.similarity_engine import SimilarityEngine
from app.repositories.book_repository import BookRepository

router = APIRouter(prefix = "/recommendation", tags = ["Recommendation"])

book_repo = BookRepository()
engine = None   

def get_engine():
    global engine
    if engine is None:
        engine = SimilarityEngine()
    return engine


@router.get(
    "/{isbn}",
    summary = "Get similar books by ISBN",
    description = (
        "Returns the top-K most similar books using cosine similarity from the "
        "recommendation engine. Includes full book metadata and similarity scores."
    ),
    response_description = "A list of recommended books with similarity scores."
)
def similar_books(isbn: str, top_k: int = 10):
    """
    Retrieve top-K similar books based on cosine similarity.
    """

    eng = get_engine()

    recs = eng.recommend_for_book(isbn, top_k = top_k)
    if not recs:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = "ISBN not found or no recommendations available")

    result = []
    for rec in recs:
        book = book_repo.get_book_by_isbn(rec["isbn"])
        if not book:
            continue

        result.append({
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

    return result
