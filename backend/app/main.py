from fastapi import FastAPI
from app.util.search import search_books


app = FastAPI()


@app.get("/search/{q}")
def search(q):
    query = q.lower()
    result = search_books(query)
    if not result:
        return {"result": [], "message": "No matching books found"}
    return {"results":result}
    




