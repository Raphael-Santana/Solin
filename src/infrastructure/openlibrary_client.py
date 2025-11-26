import httpx
from typing import Optional, Dict, Any, List
from src.core.config import settings

class OpenLibraryClient:
    def __init__(self):
        self.base_url = settings.openlibrary_base_url
        self.covers_url = settings.openlibrary_covers_url
    
    def get_cover_url(self, cover_id: Optional[int], size: str = "M") -> Optional[str]:
        """Generate cover URL. Sizes: S (small), M (medium), L (large)"""
        if not cover_id:
            return None
        return f"{self.covers_url}/id/{cover_id}-{size}.jpg"
    
    async def search_books(
        self,
        query: str,
        limit: int = 20,
        offset: int = 0,
        fields: Optional[str] = None
    ) -> Dict[str, Any]:
        """Search books in OpenLibrary"""
        async with httpx.AsyncClient() as client:
            params = {
                "q": query,
                "limit": limit,
                "offset": offset,
                "language": "eng",  # Filter for English books
            }
            if fields:
                params["fields"] = fields

            response = await client.get(f"{self.base_url}/search.json", params=params)
            response.raise_for_status()
            return response.json()
    
    async def get_trending_books(self, limit: int = 20) -> Dict[str, Any]:
        """Get trending books (most borrowed in last week)"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/trending/weekly.json",
                params={"limit": limit}
            )
            response.raise_for_status()
            return response.json()
    
    async def get_book_details(self, book_key: str) -> Dict[str, Any]:
        """Get detailed information about a specific book"""
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.base_url}{book_key}.json")
            response.raise_for_status()
            return response.json()
    
    async def get_books_by_subject(
        self,
        subject: str,
        limit: int = 20,
        offset: int = 0
    ) -> Dict[str, Any]:
        """Get books by subject/genre"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/subjects/{subject}.json",
                params={"limit": limit, "offset": offset, "language": "eng"}
            )
            response.raise_for_status()
            return response.json()
    
    async def get_author_details(self, author_key: str) -> Dict[str, Any]:
        """Get author information"""
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.base_url}{author_key}.json")
            response.raise_for_status()
            return response.json()

openlibrary_client = OpenLibraryClient()