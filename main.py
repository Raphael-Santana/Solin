from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.interface.api.routes import auth, books, user_books
from src.core.config import settings

app = FastAPI(
    title="Solin API",
    description="A Netflix-like platform for books",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(books.router, prefix="/api/v1/books", tags=["Books"])
app.include_router(user_books.router, prefix="/api/v1/user-books", tags=["User Books"])

@app.get("/")
async def root():
    return {"message": "Welcome to Solin API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}