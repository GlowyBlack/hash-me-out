from fastapi import FastAPI
from app.utils.search import search_books
from app.routers.request_router import router as request_router

app = FastAPI()
app.include_router(request_router)


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


# print(app.get("/search/Nonexistent Knight"))
print()
print(search_books("Mark"))
