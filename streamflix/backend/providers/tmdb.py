import httpx
from typing import Optional, Dict, Any

from core.config import settings


class TMDBProvider:
    """The Movie Database (TMDB) API provider."""
    
    BASE_URL = "https://api.themoviedb.org/3"
    IMAGE_BASE_URL = "https://image.tmdb.org/t/p"
    
    def __init__(self):
        self.api_key = settings.tmdb_api_key
        self.timeout = 10.0
    
    async def _request(self, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """Make a request to TMDB API."""
        url = f"{self.BASE_URL}/{endpoint}"
        
        if params is None:
            params = {}
        
        params["api_key"] = self.api_key
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            return response.json()
    
    def get_image_url(self, path: str, size: str = "w500") -> str:
        """Get full image URL from path."""
        if not path:
            return ""
        return f"{self.IMAGE_BASE_URL}/{size}{path}"
    
    async def get_popular_movies(self, page: int = 1) -> Dict[str, Any]:
        """Get popular movies."""
        return await self._request("movie/popular", {"page": page})
    
    async def get_top_rated_movies(self, page: int = 1) -> Dict[str, Any]:
        """Get top rated movies."""
        return await self._request("movie/top_rated", {"page": page})
    
    async def get_now_playing_movies(self, page: int = 1) -> Dict[str, Any]:
        """Get now playing movies."""
        return await self._request("movie/now_playing", {"page": page})
    
    async def get_upcoming_movies(self, page: int = 1) -> Dict[str, Any]:
        """Get upcoming movies."""
        return await self._request("movie/upcoming", {"page": page})
    
    async def get_movie_details(self, movie_id: int) -> Dict[str, Any]:
        """Get movie details."""
        return await self._request(f"movie/{movie_id}", {
            "append_to_response": "videos,credits,similar,recommendations"
        })
    
    async def get_popular_tv(self, page: int = 1) -> Dict[str, Any]:
        """Get popular TV shows."""
        return await self._request("tv/popular", {"page": page})
    
    async def get_top_rated_tv(self, page: int = 1) -> Dict[str, Any]:
        """Get top rated TV shows."""
        return await self._request("tv/top_rated", {"page": page})
    
    async def get_airing_today_tv(self, page: int = 1) -> Dict[str, Any]:
        """Get TV shows airing today."""
        return await self._request("tv/airing_today", {"page": page})
    
    async def get_tv_details(self, tv_id: int) -> Dict[str, Any]:
        """Get TV show details."""
        return await self._request(f"tv/{tv_id}", {
            "append_to_response": "videos,credits,similar,recommendations"
        })
    
    async def get_tv_season(self, tv_id: int, season_number: int) -> Dict[str, Any]:
        """Get TV season details."""
        return await self._request(f"tv/{tv_id}/season/{season_number}")
    
    async def get_tv_episode(
        self, tv_id: int, season_number: int, episode_number: int
    ) -> Dict[str, Any]:
        """Get TV episode details."""
        return await self._request(
            f"tv/{tv_id}/season/{season_number}/episode/{episode_number}"
        )
    
    async def search_movies(self, query: str, page: int = 1) -> Dict[str, Any]:
        """Search for movies."""
        return await self._request("search/movie", {
            "query": query,
            "page": page
        })
    
    async def search_tv(self, query: str, page: int = 1) -> Dict[str, Any]:
        """Search for TV shows."""
        return await self._request("search/tv", {
            "query": query,
            "page": page
        })
    
    async def search_multi(self, query: str, page: int = 1) -> Dict[str, Any]:
        """Search for movies and TV shows."""
        return await self._request("search/multi", {
            "query": query,
            "page": page
        })
    
    async def search_person(self, query: str, page: int = 1) -> Dict[str, Any]:
        """Search for people."""
        return await self._request("search/person", {
            "query": query,
            "page": page
        })
    
    async def get_trending(
        self, media_type: str = "all", time_window: str = "week", page: int = 1
    ) -> Dict[str, Any]:
        """Get trending content."""
        return await self._request(f"trending/{media_type}/{time_window}", {
            "page": page
        })
    
    async def get_genres(self, media_type: str = "movie") -> Dict[str, Any]:
        """Get list of genres."""
        return await self._request(f"genre/{media_type}/list")
