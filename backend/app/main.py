from fastapi import FastAPI
from app.utils.search import search_books
from app.routers.request_router import router as request_router
from app.routers.review_router import router as review_router
from app.routers.readinglist_router import router as readinglist_router
from app.routers.book_router import router as book_router

app = FastAPI()
app.include_router(request_router)
app.include_router(review_router)
app.include_router(book_router)
app.include_router(readinglist_router)

@app.get("/search/{q}")
def search(q):
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


