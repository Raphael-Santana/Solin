from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from src.domain.models import ReadingStatus

class BookBase(BaseModel):
    key: str
    title: str
    author_name: Optional[List[str]] = None
    first_publish_year: Optional[int] = None
    cover_id: Optional[int] = None
    number_of_pages: Optional[int] = None
    language: Optional[List[str]] = None

class BookDetail(BookBase):
    description: Optional[str] = None
    subjects: Optional[List[str]] = None
    isbn: Optional[List[str]] = None
    cover_url: Optional[str] = None

class BookList(BaseModel):
    books: List[BookBase]
    total: int

class UserBookCreate(BaseModel):
    book_key: str
    status: ReadingStatus

class UserBookUpdate(BaseModel):
    status: ReadingStatus

class UserBookResponse(BaseModel):
    id: int
    book_key: str
    status: ReadingStatus
    added_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class FavoriteCreate(BaseModel):
    book_key: str

class FavoriteResponse(BaseModel):
    id: int
    book_key: str
    added_at: datetime

    class Config:
        from_attributes = True

class CommentCreate(BaseModel):
    book_key: str
    content: str = Field(..., min_length=1, max_length=2000)

class CommentUpdate(BaseModel):
    content: str = Field(..., min_length=1, max_length=2000)

class CommentResponse(BaseModel):
    id: int
    book_key: str
    content: str
    created_at: datetime
    updated_at: datetime
    user_id: int
    username: str

    class Config:
        from_attributes = True