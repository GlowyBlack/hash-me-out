from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.utils.search import search_books
from app.routers.request_router import router as request_router
from app.routers import auth as auth_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=False,
)

@app.get("/")
def health_check():
    return {"status": "ok"}

app.include_router(request_router)
app.include_router(auth_router.router, prefix="/auth", tags=["auth"])
   


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
#print()
#print(search_books("Mark"))
