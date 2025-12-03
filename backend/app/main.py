from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.utils.search import search_books
from app.recommender.vectorizer_loader import GlobalVectorizer

from app.routers.recommendation_router import router as recommendation_router
from app.routers.request_router import router as request_router
from app.routers.auth import router as auth_router
from app.routers.rating_router import router as rating_router
from app.routers.review_router import router as review_router
from app.routers.readinglist_router import router as readinglist_router
from app.routers.book_router import router as book_router
from app.routers.personalized_recommendation_router import router as personalized_router


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=False,
)


app.include_router(auth_router)
app.include_router(book_router)
app.include_router(readinglist_router)
app.include_router(review_router)
app.include_router(request_router)
app.include_router(rating_router)
app.include_router(recommendation_router)
app.include_router(personalized_router)

@app.on_event("startup")
def startup_load_vectorizer():
    GlobalVectorizer.load("app/data/Enriched_Books.csv")
    return



@app.get("/")
def read_root():
    return {"message": "Welcome to my API!"}

@app.get("/search/{q}")
def search(q: str):
    query = q.lower()
    result = search_books(q)
    if not result:
        return {"result": [], "message": "No matching books found"}
    return {"results": result}
    
# For having it search as they type into textfield
# @app.get("/search")
# def search(q: str = ""):
#     query = q.lower()
#     result = search_books(q)
#     if not result:
#         return {"result": [], "message": "No matching books found"}
#     return {"results":result}



