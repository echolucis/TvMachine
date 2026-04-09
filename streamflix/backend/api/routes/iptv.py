from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from models.database import IPTVChannel
from models import get_db
from providers.iptv import IPTVProvider

router = APIRouter()
iptv_provider = IPTVProvider()


@router.get("/channels")
async def get_channels(
    group: Optional[str] = None,
    country: Optional[str] = None,
    language: Optional[str] = None,
    active: bool = True,
    db: Session = Depends(get_db)
):
    """Get list of IPTV channels."""
    query = db.query(IPTVChannel).filter(IPTVChannel.is_active == active)
    
    if group:
        query = query.filter(IPTVChannel.group.ilike(f"%{group}%"))
    
    if country:
        query = query.filter(IPTVChannel.country == country)
    
    if language:
        query = query.filter(IPTVChannel.language == language)
    
    channels = query.order_by(IPTVChannel.name).all()
    
    return {
        "total": len(channels),
        "channels": [
            {
                "id": channel.id,
                "name": channel.name,
                "logo": channel.logo,
                "group": channel.group,
                "country": channel.country,
                "language": channel.language,
                "stream_url": channel.stream_url,
            }
            for channel in channels
        ]
    }


@router.get("/channels/{channel_id}")
async def get_channel(channel_id: int, db: Session = Depends(get_db)):
    """Get a specific IPTV channel."""
    channel = db.query(IPTVChannel).filter(IPTVChannel.id == channel_id).first()
    
    if not channel:
        raise HTTPException(status_code=404, detail="Channel not found")
    
    return {
        "id": channel.id,
        "name": channel.name,
        "logo": channel.logo,
        "group": channel.group,
        "country": channel.country,
        "language": channel.language,
        "stream_url": channel.stream_url,
        "epg_id": channel.epg_id,
        "is_active": channel.is_active,
    }


@router.get("/epg/{channel_id}")
async def get_epg(
    channel_id: int,
    days: int = Query(1, ge=1, le=7),
    db: Session = Depends(get_db)
):
    """Get EPG (Electronic Program Guide) for a channel."""
    channel = db.query(IPTVChannel).filter(IPTVChannel.id == channel_id).first()
    
    if not channel:
        raise HTTPException(status_code=404, detail="Channel not found")
    
    if not channel.epg_id:
        return {"message": "No EPG available for this channel"}
    
    # TODO: Implement actual EPG fetching
    epg_data = await iptv_provider.get_epg(channel.epg_id, days=days)
    
    return epg_data


@router.post("/import-m3u")
async def import_m3u(
    url: str,
    name: str = "Imported Playlist",
    db: Session = Depends(get_db)
):
    """Import channels from M3U playlist URL."""
    try:
        channels = await iptv_provider.parse_m3u(url)
        
        imported_count = 0
        for channel_data in channels:
            # Check if channel already exists
            existing = db.query(IPTVChannel).filter(
                IPTVChannel.stream_url == channel_data["stream_url"]
            ).first()
            
            if not existing:
                channel = IPTVChannel(**channel_data)
                db.add(channel)
                imported_count += 1
        
        db.commit()
        
        return {
            "message": f"Successfully imported {imported_count} channels",
            "imported": imported_count
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to import M3U: {str(e)}")


@router.delete("/channels/{channel_id}")
async def delete_channel(channel_id: int, db: Session = Depends(get_db)):
    """Delete a channel."""
    channel = db.query(IPTVChannel).filter(IPTVChannel.id == channel_id).first()
    
    if not channel:
        raise HTTPException(status_code=404, detail="Channel not found")
    
    db.delete(channel)
    db.commit()
    
    return {"message": "Channel deleted successfully"}


@router.put("/channels/{channel_id}/toggle")
async def toggle_channel(channel_id: int, db: Session = Depends(get_db)):
    """Toggle channel active status."""
    channel = db.query(IPTVChannel).filter(IPTVChannel.id == channel_id).first()
    
    if not channel:
        raise HTTPException(status_code=404, detail="Channel not found")
    
    channel.is_active = not channel.is_active
    db.commit()
    
    return {
        "message": f"Channel {'activated' if channel.is_active else 'deactivated'}",
        "is_active": channel.is_active
    }
