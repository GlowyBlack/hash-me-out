from fastapi import FastAPI
from utils.search import search_books

app = FastAPI()


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
