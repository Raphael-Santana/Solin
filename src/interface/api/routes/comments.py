from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
from src.infrastructure.database import get_db
from src.interface.api.dependencies import get_current_user
from src.domain.models import User, Comment
from src.interface.schemas.books import CommentCreate, CommentUpdate, CommentResponse

router = APIRouter()

@router.post("", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
async def create_comment(
    comment_data: CommentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new comment on a book"""
    comment = Comment(
        user_id=current_user.id,
        book_key=comment_data.book_key,
        content=comment_data.content
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)

    # Add username to response
    response = CommentResponse(
        id=comment.id,
        book_key=comment.book_key,
        content=comment.content,
        created_at=comment.created_at,
        updated_at=comment.updated_at,
        user_id=comment.user_id,
        username=current_user.username
    )
    return response

@router.get("/book/{book_key:path}", response_model=List[CommentResponse])
async def get_book_comments(
    book_key: str,
    limit: int = Query(10, ge=1, le=50, description="Number of comments to return"),
    offset: int = Query(0, ge=0, description="Number of comments to skip"),
    db: Session = Depends(get_db)
):
    """Get comments for a specific book with pagination"""
    comments = db.query(Comment).filter(
        Comment.book_key == book_key
    ).order_by(Comment.created_at.desc()).offset(offset).limit(limit).all()

    # Build response with usernames
    response = []
    for comment in comments:
        response.append(CommentResponse(
            id=comment.id,
            book_key=comment.book_key,
            content=comment.content,
            created_at=comment.created_at,
            updated_at=comment.updated_at,
            user_id=comment.user_id,
            username=comment.user.username
        ))

    return response

@router.put("/{comment_id}", response_model=CommentResponse)
async def update_comment(
    comment_id: int,
    comment_update: CommentUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a comment (only by the comment author)"""
    comment = db.query(Comment).filter(Comment.id == comment_id).first()

    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")

    if comment.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this comment")

    comment.content = comment_update.content
    db.commit()
    db.refresh(comment)

    response = CommentResponse(
        id=comment.id,
        book_key=comment.book_key,
        content=comment.content,
        created_at=comment.created_at,
        updated_at=comment.updated_at,
        user_id=comment.user_id,
        username=current_user.username
    )
    return response

@router.delete("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(
    comment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a comment (only by the comment author)"""
    comment = db.query(Comment).filter(Comment.id == comment_id).first()

    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")

    if comment.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this comment")

    db.delete(comment)
    db.commit()
