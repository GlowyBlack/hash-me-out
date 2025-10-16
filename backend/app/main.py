from fastapi import FastAPI
from util.search import search_books
import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))


app = FastAPI()


# @app.get("/search")
# def search(q: str = ""):
#     query = q.lower()
#     result = search_books(q)
#     if not result:
#         return {"result": [], "message": "No matching books found"}
#     return {"results":result}
    




