from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, ForeignKey, Text, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os

# Database URL from environment or default
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://streamflix:streamflix_password@db:5432/streamflix")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    watchlist = relationship("WatchlistItem", back_populates="user", cascade="all, delete-orphan")
    watch_history = relationship("WatchHistory", back_populates="user", cascade="all, delete-orphan")


class Movie(Base):
    __tablename__ = "movies"
    
    id = Column(Integer, primary_key=True, index=True)
    tmdb_id = Column(Integer, unique=True, index=True)
    title = Column(String, nullable=False)
    overview = Column(Text)
    poster_path = Column(String)
    backdrop_path = Column(String)
    release_date = Column(String)
    runtime = Column(Integer)
    rating = Column(Float)
    genres = Column(String)  # JSON string
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    streaming_sources = relationship("StreamingSource", back_populates="movie", cascade="all, delete-orphan")


class TVShow(Base):
    __tablename__ = "tv_shows"
    
    id = Column(Integer, primary_key=True, index=True)
    tmdb_id = Column(Integer, unique=True, index=True)
    name = Column(String, nullable=False)
    overview = Column(Text)
    poster_path = Column(String)
    backdrop_path = Column(String)
    first_air_date = Column(String)
    last_air_date = Column(String)
    rating = Column(Float)
    genres = Column(String)  # JSON string
    number_of_seasons = Column(Integer)
    number_of_episodes = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    seasons = relationship("Season", order_by=lambda: Season.season_number, back_populates="tv_show", cascade="all, delete-orphan")


class Season(Base):
    __tablename__ = "seasons"
    
    id = Column(Integer, primary_key=True, index=True)
    tv_show_id = Column(Integer, ForeignKey("tv_shows.id"), nullable=False)
    season_number = Column(Integer, nullable=False)
    name = Column(String)
    overview = Column(Text)
    poster_path = Column(String)
    air_date = Column(String)
    episode_count = Column(Integer)
    
    # Relationships
    episodes = relationship("Episode", back_populates="season", cascade="all, delete-orphan")
    tv_show = relationship("TVShow", back_populates="seasons")


class Episode(Base):
    __tablename__ = "episodes"
    
    id = Column(Integer, primary_key=True, index=True)
    season_id = Column(Integer, ForeignKey("seasons.id"), nullable=False)
    episode_number = Column(Integer, nullable=False)
    name = Column(String, nullable=False)
    overview = Column(Text)
    still_path = Column(String)
    air_date = Column(String)
    runtime = Column(Integer)
    rating = Column(Float)
    
    # Relationships
    season = relationship("Season", back_populates="episodes")
    streaming_sources = relationship("StreamingSource", back_populates="episode", cascade="all, delete-orphan")


class StreamingSource(Base):
    __tablename__ = "streaming_sources"
    
    id = Column(Integer, primary_key=True, index=True)
    episode_id = Column(Integer, ForeignKey("episodes.id"), nullable=True)
    movie_id = Column(Integer, ForeignKey("movies.id"), nullable=True)
    provider_name = Column(String, nullable=False)
    quality = Column(String, default="HD")
    language = Column(String, default="en")
    url = Column(String, nullable=False)
    type = Column(String)  # 'torrent', 'direct', 'hls', etc.
    size = Column(String)
    seeds = Column(Integer)
    peers = Column(Integer)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    episode = relationship("Episode", back_populates="streaming_sources")
    movie = relationship("Movie", back_populates="streaming_sources")


class WatchlistItem(Base):
    __tablename__ = "watchlist_items"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    movie_id = Column(Integer, ForeignKey("movies.id"), nullable=True)
    tv_show_id = Column(Integer, ForeignKey("tv_shows.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="watchlist")


class WatchHistory(Base):
    __tablename__ = "watch_history"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    movie_id = Column(Integer, ForeignKey("movies.id"), nullable=True)
    episode_id = Column(Integer, ForeignKey("episodes.id"), nullable=True)
    watched_at = Column(DateTime, default=datetime.utcnow)
    progress = Column(Integer, default=0)  # Progress in seconds
    
    # Relationships
    user = relationship("User", back_populates="watch_history")


class IPTVChannel(Base):
    __tablename__ = "iptv_channels"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    logo = Column(String)
    group = Column(String)
    country = Column(String)
    language = Column(String)
    stream_url = Column(String, nullable=False)
    epg_id = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
