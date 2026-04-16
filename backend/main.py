"""
Phase 5 & 6: Backend API & Search Engine
FastAPI backend with endpoints for channels, guide, search, and streaming.
"""
from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, JSONResponse
from pathlib import Path
from typing import List, Optional, Dict
from datetime import datetime, timezone, timedelta
import json
import httpx

app = FastAPI(title="IPTV/EPG API", version="1.0.0")

# CORS for browser playback
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Data paths
DATA_DIR = Path(__file__).parent / "data"
CHANNELS_FILE = DATA_DIR / "channels.json"
EPG_FILE = DATA_DIR / "epg.json"
GUIDE_REGISTRY_FILE = DATA_DIR / "guide_registry.json"

# In-memory cache (refresh on each request in production, or use background tasks)
_channels_cache: Optional[List[dict]] = None
_epg_cache: Optional[Dict[str, List[dict]]] = None
_registry_cache: Optional[Dict[str, dict]] = None


def load_json_file(filepath: Path):
    """Load JSON file with caching."""
    if not filepath.exists():
        return None
    
    with open(filepath, 'r') as f:
        return json.load(f)


def get_channels() -> List[dict]:
    """Get all channels."""
    global _channels_cache
    if _channels_cache is None:
        _channels_cache = load_json_file(CHANNELS_FILE) or []
    return _channels_cache


def get_epg() -> Dict[str, List[dict]]:
    """Get EPG data."""
    global _epg_cache
    if _epg_cache is None:
        _epg_cache = load_json_file(EPG_FILE) or {}
    return _epg_cache


def get_registry() -> Dict[str, dict]:
    """Get guide registry."""
    global _registry_cache
    if _registry_cache is None:
        _registry_cache = load_json_file(GUIDE_REGISTRY_FILE) or {}
    return _registry_cache


@app.get("/api/health")
async def health_check():
    """Health check endpoint with system stats."""
    channels = get_channels()
    epg = get_epg()
    registry = get_registry()
    
    active_channels = sum(1 for ch in channels if ch.get('status') == 'active')
    
    # Calculate EPG coverage hours
    total_hours = 0
    now = datetime.now(timezone.utc)
    for channel_id, programmes in epg.items():
        for prog in programmes:
            try:
                end = datetime.fromisoformat(prog['end_utc'].replace('Z', '+00:00'))
                if end > now:
                    start = datetime.fromisoformat(prog['start_utc'].replace('Z', '+00:00'))
                    total_hours += (end - start).total_seconds() / 3600
            except:
                pass
    
    avg_hours_per_channel = total_hours / len(epg) if epg else 0
    
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "channels_total": len(channels),
        "channels_active": active_channels,
        "epg_channels": len(epg),
        "epg_coverage_hours": round(avg_hours_per_channel, 1),
        "mapped_channels": len(registry),
    }


@app.get("/api/channels")
async def list_channels(
    status: Optional[str] = Query(None, description="Filter by status: active/dead"),
    group: Optional[str] = Query(None, description="Filter by group/category"),
    limit: int = Query(100, ge=1, le=1000),
):
    """List channels with optional filtering."""
    channels = get_channels()
    
    # Filter by status
    if status:
        channels = [ch for ch in channels if ch.get('status') == status]
    
    # Filter by group
    if group:
        channels = [ch for ch in channels if ch.get('group', '').lower() == group.lower()]
    
    # Limit results
    channels = channels[:limit]
    
    return {"channels": channels, "total": len(channels)}


@app.get("/api/guide")
async def get_guide(
    channel_id: str = Query(..., description="Channel ID"),
    start: Optional[str] = Query(None, description="Start time (ISO 8601)"),
    end: Optional[str] = Query(None, description="End time (ISO 8601)"),
):
    """Get EPG programmes for a specific channel and time range."""
    epg = get_epg()
    
    if channel_id not in epg:
        # Try to find in registry
        registry = get_registry()
        for ch_id, data in registry.items():
            if data.get('epg_channel_id') == channel_id:
                channel_id = data['epg_channel_id']
                break
        else:
            raise HTTPException(status_code=404, detail=f"Channel '{channel_id}' not found")
    
    programmes = epg[channel_id]
    
    # Parse time range
    now = datetime.now(timezone.utc)
    try:
        start_time = datetime.fromisoformat(start.replace('Z', '+00:00')) if start else now
        end_time = datetime.fromisoformat(end.replace('Z', '+00:00')) if end else now + timedelta(hours=2)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid time format: {e}")
    
    # Filter programmes in time range
    start_str = start_time.isoformat()
    end_str = end_time.isoformat()
    
    filtered = [
        p for p in programmes
        if p['end_utc'] > start_str and p['start_utc'] < end_str
    ]
    
    return {
        "channel_id": channel_id,
        "start": start_str,
        "end": end_str,
        "programmes": filtered,
        "total": len(filtered)
    }


@app.get("/api/search")
async def search_programs(
    q: str = Query(..., description="Search query"),
    type: Optional[str] = Query(None, description="Search type: title/description/category"),
    genre: Optional[str] = Query(None, description="Filter by genre/category"),
    after: Optional[str] = Query(None, description="Search programmes after this time"),
    before: Optional[str] = Query(None, description="Search programmes before this time"),
    limit: int = Query(20, ge=1, le=100),
):
    """Search programmes across all channels."""
    epg = get_epg()
    query_lower = q.lower()
    
    # Parse time filters
    now = datetime.now(timezone.utc)
    try:
        after_time = datetime.fromisoformat(after.replace('Z', '+00:00')) if after else now
        before_time = datetime.fromisoformat(before.replace('Z', '+00:00')) if before else now + timedelta(days=7)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid time format: {e}")
    
    after_str = after_time.isoformat()
    before_str = before_time.isoformat()
    
    results = []
    
    for channel_id, programmes in epg.items():
        for prog in programmes:
            # Time filter
            if prog['start_utc'] < after_str or prog['start_utc'] > before_str:
                continue
            
            # Genre filter
            if genre and genre.lower() not in [c.lower() for c in prog.get('category', [])]:
                continue
            
            # Text search
            match = False
            if type == 'title':
                match = query_lower in prog.get('title', '').lower()
            elif type == 'description':
                match = query_lower in prog.get('description', '').lower()
            elif type == 'category':
                match = any(query_lower in c.lower() for c in prog.get('category', []))
            else:
                # Search all fields
                match = (
                    query_lower in prog.get('title', '').lower() or
                    query_lower in prog.get('description', '').lower() or
                    any(query_lower in c.lower() for c in prog.get('category', []))
                )
            
            if match:
                results.append({
                    **prog,
                    'channel_id': channel_id
                })
                
                if len(results) >= limit:
                    return {"results": results, "total": len(results)}
    
    return {"results": results, "total": len(results)}


@app.get("/api/stream/{channel_id}")
async def get_stream(channel_id: str, request: Request):
    """
    Get stream URL for a channel.
    Returns 302 redirect to the actual stream URL.
    """
    channels = get_channels()
    
    # Find channel
    channel = next((ch for ch in channels if ch['id'] == channel_id), None)
    
    if not channel:
        # Try registry
        registry = get_registry()
        if channel_id in registry:
            channel = registry[channel_id].get('channel')
    
    if not channel:
        raise HTTPException(status_code=404, detail=f"Channel '{channel_id}' not found")
    
    if channel.get('status') == 'dead':
        raise HTTPException(status_code=410, detail="Stream is currently unavailable")
    
    stream_url = channel.get('url')
    if not stream_url:
        raise HTTPException(status_code=404, detail="Stream URL not found")
    
    # Redirect to stream URL
    return RedirectResponse(url=stream_url)


@app.get("/api/channel/{channel_id}")
async def get_channel_details(channel_id: str):
    """Get detailed information about a specific channel."""
    registry = get_registry()
    
    if channel_id not in registry:
        # Try to find by channel ID in channels list
        channels = get_channels()
        channel = next((ch for ch in channels if ch['id'] == channel_id), None)
        if channel:
            return {"channel": channel, "programmes": []}
        raise HTTPException(status_code=404, detail=f"Channel '{channel_id}' not found")
    
    data = registry[channel_id]
    
    # Get current and next programmes
    now = datetime.now(timezone.utc)
    now_str = now.isoformat()
    
    current_prog = None
    next_prog = None
    
    for prog in data.get('programmes', []):
        if prog['start_utc'] <= now_str < prog['end_utc']:
            current_prog = prog
        elif prog['start_utc'] > now_str and next_prog is None:
            next_prog = prog
            break
    
    return {
        "channel": data['channel'],
        "epg_channel_id": data['epg_channel_id'],
        "current_programme": current_prog,
        "next_programme": next_prog,
        "total_programmes": len(data.get('programmes', []))
    }


@app.get("/api/groups")
async def list_groups():
    """List all unique channel groups/categories."""
    channels = get_channels()
    groups = set(ch.get('group', 'Unknown') for ch in channels if ch.get('group'))
    return {"groups": sorted(list(groups))}


# Background task to refresh caches (optional)
@app.on_event("startup")
async def startup_event():
    """Initialize caches on startup."""
    global _channels_cache, _epg_cache, _registry_cache
    print("[API] Loading data caches...")
    _channels_cache = None
    _epg_cache = None
    _registry_cache = None
    print("[API] Ready to serve requests")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
