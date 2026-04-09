from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from models import get_db
from providers.tmdb import TMDBProvider

router = APIRouter()
tmdb = TMDBProvider()


@router.get("/movies")
async def get_movies(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    genre: Optional[str] = None,
    year: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Get list of movies with optional filters."""
    # TODO: Implement database query
    # For now, return from TMDB
    try:
        movies = await tmdb.get_popular_movies(page=page)
        return {
            "page": page,
            "total_pages": movies.get("total_pages", 0),
            "total_results": movies.get("total_results", 0),
            "results": movies.get("results", [])
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/movies/{movie_id}")
async def get_movie(movie_id: int, db: Session = Depends(get_db)):
    """Get movie details by ID."""
    try:
        movie = await tmdb.get_movie_details(movie_id)
        if not movie:
            raise HTTPException(status_code=404, detail="Movie not found")
        return movie
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tv")
async def get_tv_shows(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    genre: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get list of TV shows with optional filters."""
    try:
        tv_shows = await tmdb.get_popular_tv(page=page)
        return {
            "page": page,
            "total_pages": tv_shows.get("total_pages", 0),
            "total_results": tv_shows.get("total_results", 0),
            "results": tv_shows.get("results", [])
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tv/{tv_id}")
async def get_tv_show(tv_id: int, db: Session = Depends(get_db)):
    """Get TV show details by ID."""
    try:
        tv_show = await tmdb.get_tv_details(tv_id)
        if not tv_show:
            raise HTTPException(status_code=404, detail="TV show not found")
        return tv_show
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tv/{tv_id}/season/{season_number}")
async def get_season(
    tv_id: int,
    season_number: int,
    db: Session = Depends(get_db)
):
    """Get season details for a TV show."""
    try:
        season = await tmdb.get_tv_season(tv_id, season_number)
        if not season:
            raise HTTPException(status_code=404, detail="Season not found")
        return season
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/search")
async def search(
    q: str = Query(..., min_length=1),
    type: str = Query("multi", regex="^(movie|tv|multi)$"),
    page: int = Query(1, ge=1),
    db: Session = Depends(get_db)
):
    """Search for movies and/or TV shows."""
    try:
        if type == "multi":
            results = await tmdb.search_multi(q, page=page)
        elif type == "movie":
            results = await tmdb.search_movies(q, page=page)
        else:
            results = await tmdb.search_tv(q, page=page)
        
        return {
            "page": page,
            "total_pages": results.get("total_pages", 0),
            "total_results": results.get("total_results", 0),
            "results": results.get("results", [])
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/trending")
async def get_trending(
    time_window: str = Query("week", regex="^(day|week)$"),
    media_type: str = Query("all", regex="^(all|movie|tv)$"),
    page: int = Query(1, ge=1),
    db: Session = Depends(get_db)
):
    """Get trending content."""
    try:
        trending = await tmdb.get_trending(media_type, time_window, page=page)
        return {
            "page": page,
            "total_pages": trending.get("total_pages", 0),
            "total_results": trending.get("total_results", 0),
            "results": trending.get("results", [])
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
