from fastapi import APIRouter, Query, HTTPException
from typing import Optional, List, Dict, Any
from src.infrastructure.openlibrary_client import openlibrary_client
import random

router = APIRouter()


def transform_book_for_frontend(book_data: Dict[str, Any]) -> Dict[str, Any]:
    """Transform OpenLibrary data to frontend-expected format"""
    # Get only the primary (first) author to keep cards compact
    author_name = book_data.get("author_name", [])
    primary_author = author_name[0] if author_name else "Unknown Author"

    return {
        "id": book_data.get("key", ""),  # Use key as id
        "title": book_data.get("title", ""),
        "author": primary_author,
        "genre": book_data.get("subjects", ["General"])[0] if book_data.get("subjects") else "General",
        "publication_year": book_data.get("first_publish_year"),
        "pages": book_data.get("number_of_pages"),
        "cover_url": book_data.get("cover_url"),
        "description": book_data.get("description", ""),
        # Keep original fields for compatibility
        "key": book_data.get("key"),
        "author_name": book_data.get("author_name"),
        "subjects": book_data.get("subjects"),
    }

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
                "subjects": [],
            }
            books.append(transform_book_for_frontend(book))

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
                "subjects": [],
            }
            books.append(transform_book_for_frontend(book))

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
                "subjects": [subject.replace("_", " ").title()],
            }
            books.append(transform_book_for_frontend(book))

        return {
            "books": books,
            "total": result.get("work_count", 0),
            "subject": subject,
            "offset": offset,
            "limit": limit
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/featured")
async def get_featured_book():
    """Get the featured book (The Lord of the Rings)"""
    try:
        book_key = "/works/OL27448W"  # The Lord of the Rings
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

        result = {
            "key": book_data.get("key"),
            "title": book_data.get("title"),
            "author_name": authors,
            "description": description,
            "subjects": book_data.get("subjects", [])[:20],
            "first_publish_year": book_data.get("first_publish_date"),
            "cover_id": cover_id,
            "cover_url": openlibrary_client.get_cover_url(cover_id, size="L"),
        }

        return transform_book_for_frontend(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to fetch featured book")


@router.get("/most-read")
async def get_most_read_books(limit: int = Query(20, ge=1, le=100)):
    """Get most read books from popular fiction subjects"""
    try:
        # Use popular fiction subjects to get different books than trending
        subjects = ["fiction", "classics", "literature", "bestseller"]
        all_books = []

        for subject in subjects:
            result = await openlibrary_client.get_books_by_subject(
                subject=subject,
                limit=10,
                offset=0
            )

            for work in result.get("works", [])[:5]:
                # Get only the primary author
                authors = work.get("authors", [])
                author_name = [authors[0].get("name")] if authors else []

                book = {
                    "key": work.get("key"),
                    "title": work.get("title"),
                    "author_name": author_name,
                    "first_publish_year": work.get("first_publish_year"),
                    "cover_id": work.get("cover_id"),
                    "cover_url": openlibrary_client.get_cover_url(work.get("cover_id")),
                    "subjects": [subject.replace("_", " ").title()],
                }
                all_books.append(transform_book_for_frontend(book))

        # Shuffle and limit
        random.shuffle(all_books)

        return {"books": all_books[:limit], "total": len(all_books[:limit])}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/explore")
async def get_explore_books(limit: int = Query(50, ge=1, le=100)):
    """Get books for exploration across multiple genres"""
    try:
        # Fetch books from multiple popular subjects
        subjects = ["fantasy", "science_fiction", "romance", "mystery", "thriller", "history"]
        all_books = []

        for subject in subjects:
            result = await openlibrary_client.get_books_by_subject(
                subject=subject,
                limit=10,
                offset=0
            )

            for work in result.get("works", [])[:8]:
                # Get only the primary author (first one)
                authors = work.get("authors", [])
                author_name = [authors[0].get("name")] if authors else []

                book = {
                    "key": work.get("key"),
                    "title": work.get("title"),
                    "author_name": author_name,
                    "first_publish_year": work.get("first_publish_year"),
                    "cover_id": work.get("cover_id"),
                    "cover_url": openlibrary_client.get_cover_url(work.get("cover_id")),
                    "subjects": [subject.replace("_", " ").title()],
                }
                all_books.append(transform_book_for_frontend(book))

        # Shuffle for variety and limit
        random.shuffle(all_books)

        return {"books": all_books[:limit], "total": len(all_books[:limit])}
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

        result = {
            "key": book_data.get("key"),
            "title": book_data.get("title"),
            "author_name": authors,
            "description": description,
            "subjects": book_data.get("subjects", [])[:20],
            "first_publish_year": book_data.get("first_publish_date"),
            "cover_id": cover_id,
            "cover_url": openlibrary_client.get_cover_url(cover_id, size="L"),
        }

        return transform_book_for_frontend(result)
    except Exception as e:
        raise HTTPException(status_code=404, detail="Book not found")