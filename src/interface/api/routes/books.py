from fastapi import APIRouter, Query, HTTPException
from typing import Optional, List
from src.infrastructure.openlibrary_client import openlibrary_client

router = APIRouter()

@router.get("/search")
async def search_books(
    q: str = Query(..., description="Search query"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """Search for books"""
    try:
        result = await openlibrary_client.search_books(
            query=q,
            limit=limit,
            offset=offset
        )
        
        books = []
        for doc in result.get("docs", []):
            book = {
                "key": doc.get("key"),
                "title": doc.get("title"),
                "author_name": doc.get("author_name"),
                "first_publish_year": doc.get("first_publish_year"),
                "cover_id": doc.get("cover_i"),
                "cover_url": openlibrary_client.get_cover_url(doc.get("cover_i")),
                "number_of_pages": doc.get("number_of_pages_median"),
                "language": doc.get("language"),
            }
            books.append(book)
        
        return {
            "books": books,
            "total": result.get("numFound", 0),
            "offset": offset,
            "limit": limit
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/trending")
async def get_trending_books(limit: int = Query(20, ge=1, le=100)):
    """Get trending books (most popular this week)"""
    try:
        result = await openlibrary_client.get_trending_books(limit=limit)
        
        books = []
        for work in result.get("works", []):
            book = {
                "key": work.get("key"),
                "title": work.get("title"),
                "author_name": work.get("author_name"),
                "first_publish_year": work.get("first_publish_year"),
                "cover_id": work.get("cover_i"),
                "cover_url": openlibrary_client.get_cover_url(work.get("cover_i")),
            }
            books.append(book)
        
        return {"books": books, "total": len(books)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/subjects/{subject}")
async def get_books_by_subject(
    subject: str,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """Get books by genre/subject (e.g., 'fantasy', 'science_fiction', 'romance')"""
    try:
        result = await openlibrary_client.get_books_by_subject(
            subject=subject,
            limit=limit,
            offset=offset
        )
        
        books = []
        for work in result.get("works", []):
            book = {
                "key": work.get("key"),
                "title": work.get("title"),
                "author_name": [a.get("name") for a in work.get("authors", [])],
                "first_publish_year": work.get("first_publish_year"),
                "cover_id": work.get("cover_id"),
                "cover_url": openlibrary_client.get_cover_url(work.get("cover_id")),
            }
            books.append(book)
        
        return {
            "books": books,
            "total": result.get("work_count", 0),
            "subject": subject,
            "offset": offset,
            "limit": limit
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{book_key:path}")
async def get_book_details(book_key: str):
    """Get detailed information about a specific book"""
    try:
        # Ensure the key starts with /works/ or /books/
        if not book_key.startswith("/"):
            book_key = f"/works/{book_key}"
        
        book_data = await openlibrary_client.get_book_details(book_key)
        
        # Extract authors
        authors = []
        if "authors" in book_data:
            for author in book_data["authors"]:
                author_key = author.get("author", {}).get("key")
                if author_key:
                    try:
                        author_data = await openlibrary_client.get_author_details(author_key)
                        authors.append(author_data.get("name"))
                    except:
                        pass
        
        # Handle description
        description = None
        if "description" in book_data:
            if isinstance(book_data["description"], dict):
                description = book_data["description"].get("value")
            else:
                description = book_data["description"]
        
        # Get covers
        covers = book_data.get("covers", [])
        cover_id = covers[0] if covers else None
        
        return {
            "key": book_data.get("key"),
            "title": book_data.get("title"),
            "author_name": authors,
            "description": description,
            "subjects": book_data.get("subjects", [])[:20],
            "first_publish_year": book_data.get("first_publish_date"),
            "cover_id": cover_id,
            "cover_url": openlibrary_client.get_cover_url(cover_id, size="L"),
        }
    except Exception as e:
        raise HTTPException(status_code=404, detail="Book not found")