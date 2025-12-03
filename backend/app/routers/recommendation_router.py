from datetime import datetime
from fastapi import APIRouter, HTTPException, status
from app.recommender.similarity_engine import SimilarityEngine
from app.repositories.book_repository import BookRepository
from app.logger import logger
from app.utils.normalize import normalize_text

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
@router.get("/{isbn}")
def similar_books(isbn: str, top_k: int = 10):
    start = datetime.now()
    logger.info(f"API CALL      | /recommendation/{isbn} | top_k={top_k}")

    input_book = book_repo.get_book_by_isbn(isbn)
    if not input_book:
        raise HTTPException(status_code=404, detail="Input ISBN not found")

    input_key = (
        normalize_text(input_book["Book-Title"]),
        normalize_text(input_book["Book-Author"])
    )

    eng = get_engine()
    recs = eng.recommend_for_book(isbn, top_k=top_k)

    if not recs:
        logger.warning(f"API NOTFOUND  | /recommendation/{isbn} | no similar books")
        raise HTTPException(
            status_code=404,
            detail="ISBN not found or no recommendations available"
        )

    seen_titles = set()
    results = []

    for rec in recs:
        book = book_repo.get_book_by_isbn(rec["isbn"])
        if not book:
            logger.warning(f"SKIP          | missing metadata | isbn={rec['isbn']}")
            continue

        key = (
            normalize_text(book["Book-Title"]),
            normalize_text(book["Book-Author"]),
        )

        # 🔥 Prevent recommending the *same book* (different ISBN)
        if key == input_key:
            logger.info(f"SKIP INPUT    | same book | isbn={book['ISBN']}")
            continue

        # prevent duplicates inside results
        if key in seen_titles:
            logger.info(f"DEDUP         | {book['Book-Title']} by {book['Book-Author']}")
            continue

        seen_titles.add(key)

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
