from datetime import datetime
from fastapi import APIRouter, HTTPException, status
from app.recommender.similarity_engine import SimilarityEngine
from app.repositories.book_repository import BookRepository
from app.logger import logger
from app.utils.book_identity import (
    normalize_text,
    normalize_title_for_work,
    is_same_work,
)

router = APIRouter(
    prefix = "/recommendation",
    tags = ["Recommendation"]
)

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
def similar_books(isbn: str, top_k: int = 12):
    start = datetime.now()
    logger.info(f"API CALL      | /recommendation/{isbn} | top_k={top_k}")

    input_book = book_repo.get_book_by_isbn(isbn)
    if not input_book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Input ISBN not found"
        )

    eng = get_engine()
    recs = eng.recommend_for_book(isbn, top_k=top_k)

    if not recs:
        logger.warning(f"API NOTFOUND  | /recommendation/{isbn} | no similar books")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="ISBN not found or no recommendations available"
        )

    # Work-level dedup (remove multiple ISBNs of same book)
    seen_works = set()

    results = []

    for rec in recs:
        book = book_repo.get_book_by_isbn(rec["isbn"])
        if not book:
            logger.warning(f"SKIP          | missing metadata | isbn={rec['isbn']}")
            continue

        # Skip same underlying work as the input
        if is_same_work(input_book, book):
            logger.info(f"SKIP SAMEWORK | isbn={book['ISBN']}")
            continue

        # ---- Work-level dedup (title + author last name) ----
        title_key = normalize_title_for_work(book["Book-Title"])

        author_norm = normalize_text(book["Book-Author"])
        last_name = author_norm.split()[-1] if author_norm else ""

        work_key = (title_key, last_name)

        if work_key in seen_works:
            logger.info(f"DEDUP WORK    | {book['Book-Title']} by {book['Book-Author']}")
            continue

        seen_works.add(work_key)

        # ---- Append result ----
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

    elapsed = (datetime.now() - start).total_seconds() * 1000
    logger.info(
        f"API DONE      | /recommendation/{isbn} | returned={len(results)} | took={elapsed:.2f}ms"
    )

    return results
