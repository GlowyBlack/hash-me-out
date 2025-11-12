from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.utils.search import search_books
from app.routers.request_router import router as request_router
from app.routers import auth as auth_router
from app.routers.review_router import router as review_router

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

# Routers
app.include_router(request_router)
app.include_router(auth_router.router, prefix="/auth", tags=["auth"])
app.include_router(review_router)

@app.get("/search/{q}")
def search(q: str):
    query = q.lower()
    result = search_books(q)
    if not result:
        return {"result": [], "message": "No matching books found"}
    return {"results": result}

