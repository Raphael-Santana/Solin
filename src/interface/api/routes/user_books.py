from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from src.infrastructure.database import get_db
from src.interface.api.dependencies import get_current_user
from src.domain.models import User, UserBook, Favorite, ReadingStatus
from src.interface.schemas.books import (
    UserBookCreate,
    UserBookUpdate,
    UserBookResponse,
    FavoriteCreate,
    FavoriteResponse
)

router = APIRouter()

# User Books (Reading Status) Endpoints

@router.post("/reading-list", response_model=UserBookResponse, status_code=status.HTTP_201_CREATED)
async def add_to_reading_list(
    book_data: UserBookCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add a book to user's reading list with status (want_to_read, reading, read)"""
    # Check if book already exists
    existing = db.query(UserBook).filter(
        UserBook.user_id == current_user.id,
        UserBook.book_key == book_data.book_key
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Book already in your reading list"
        )
    
    user_book = UserBook(
        user_id=current_user.id,
        book_key=book_data.book_key,
        status=book_data.status
    )
    db.add(user_book)
    db.commit()
    db.refresh(user_book)
    return user_book

@router.get("/reading-list", response_model=List[UserBookResponse])
async def get_reading_list(
    status: Optional[ReadingStatus] = Query(None, description="Filter by status"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's reading list, optionally filtered by status"""
    query = db.query(UserBook).filter(UserBook.user_id == current_user.id)
    
    if status:
        query = query.filter(UserBook.status == status)
    
    return query.order_by(UserBook.updated_at.desc()).all()

@router.put("/reading-list/{book_key:path}", response_model=UserBookResponse)
async def update_reading_status(
    book_key: str,
    book_update: UserBookUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update reading status of a book"""
    user_book = db.query(UserBook).filter(
        UserBook.user_id == current_user.id,
        UserBook.book_key == book_key
    ).first()
    
    if not user_book:
        raise HTTPException(status_code=404, detail="Book not found in reading list")
    
    user_book.status = book_update.status
    db.commit()
    db.refresh(user_book)
    return user_book

@router.delete("/reading-list/{book_key:path}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_from_reading_list(
    book_key: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Remove a book from reading list"""
    user_book = db.query(UserBook).filter(
        UserBook.user_id == current_user.id,
        UserBook.book_key == book_key
    ).first()
    
    if not user_book:
        raise HTTPException(status_code=404, detail="Book not found in reading list")
    
    db.delete(user_book)
    db.commit()

# Favorites Endpoints

@router.post("/favorites", response_model=FavoriteResponse, status_code=status.HTTP_201_CREATED)
async def add_to_favorites(
    favorite_data: FavoriteCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add a book to favorites"""
    existing = db.query(Favorite).filter(
        Favorite.user_id == current_user.id,
        Favorite.book_key == favorite_data.book_key
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Book already in favorites"
        )
    
    favorite = Favorite(
        user_id=current_user.id,
        book_key=favorite_data.book_key
    )
    db.add(favorite)
    db.commit()
    db.refresh(favorite)
    return favorite

@router.get("/favorites", response_model=List[FavoriteResponse])
async def get_favorites(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's favorite books"""
    return db.query(Favorite).filter(
        Favorite.user_id == current_user.id
    ).order_by(Favorite.added_at.desc()).all()

@router.delete("/favorites/{book_key:path}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_from_favorites(
    book_key: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Remove a book from favorites"""
    favorite = db.query(Favorite).filter(
        Favorite.user_id == current_user.id,
        Favorite.book_key == book_key
    ).first()
    
    if not favorite:
        raise HTTPException(status_code=404, detail="Book not found in favorites")
    
    db.delete(favorite)
    db.commit()