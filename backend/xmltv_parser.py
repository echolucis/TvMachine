"""
Phase 3: XMLTV EPG Parser
Parse program schedules and index them for fast time-based queries.
Uses streaming XML parser to handle large files efficiently.
"""
import asyncio
from pathlib import Path
from typing import List, Dict, Optional, Generator
from dataclasses import dataclass, asdict
from datetime import datetime, timezone, timedelta
import xml.etree.ElementTree as ET
import json

RAW_XMLTV_FILE = Path(__file__).parent / "data" / "raw" / "xmltv" / "guide.xml"
EPG_DB_FILE = Path(__file__).parent / "data" / "epg.json"


@dataclass
class Programme:
    channel_id: str
    title: str
    description: Optional[str]
    start_utc: str  # ISO 8601 format
    end_utc: str
    category: List[str]
    episode: Optional[str]
    
    def to_dict(self) -> dict:
        return asdict(self)


def parse_xmltv_datetime(dt_str: str) -> datetime:
    """
    Parse XMLTV datetime format to UTC datetime.
    XMLTV format: 20240615180000 +0100 or 20240615180000 UTC
    """
    # Remove timezone suffix and parse
    parts = dt_str.strip().split()
    dt_part = parts[0]
    tz_part = parts[1] if len(parts) > 1 else 'UTC'
    
    # Parse datetime: YYYYMMDDHHMMSS
    dt = datetime.strptime(dt_part, "%Y%m%d%H%M%S")
    
    # Handle timezone
    if tz_part == 'UTC':
        dt = dt.replace(tzinfo=timezone.utc)
    else:
        # Parse offset like +0100 or -0500
        sign = 1 if tz_part[0] == '+' else -1
        hours = int(tz_part[1:3])
        minutes = int(tz_part[3:5])
        offset = timedelta(hours=sign * hours, minutes=sign * minutes)
        tz = timezone(offset)
        dt = dt.replace(tzinfo=tz)
        # Convert to UTC
        dt = dt.astimezone(timezone.utc)
    
    return dt


def stream_xml_programmes(filepath: Path) -> Generator[Programme, None, None]:
    """
    Stream-parse XMLTV file using iterparse to avoid loading entire file into memory.
    Yields Programme objects one at a time.
    """
    context = ET.iterparse(filepath, events=('end',))
    
    for event, elem in context:
        if elem.tag != 'programme':
            continue
            
        try:
            # Extract channel ID
            channel_id = elem.get('channel', '')
            
            # Extract title
            title_elem = elem.find('title')
            title = title_elem.text if title_elem is not None and title_elem.text else "Unknown"
            
            # Extract description
            desc_elem = elem.find('desc')
            description = desc_elem.text if desc_elem is not None and desc_elem.text else None
            
            # Extract timestamps
            start_elem = elem.find('start')
            stop_elem = elem.find('stop')
            
            if start_elem is None or stop_elem is None:
                continue
            
            start_utc = parse_xmltv_datetime(start_elem.text)
            end_utc = parse_xmltv_datetime(stop_elem.text)
            
            # Extract categories
            categories = []
            for cat_elem in elem.findall('category'):
                if cat_elem.text:
                    categories.append(cat_elem.text)
            
            # Extract episode info
            episode_elem = elem.find('episode-num')
            episode = episode_elem.text if episode_elem is not None and episode_elem.text else None
            
            yield Programme(
                channel_id=channel_id,
                title=title,
                description=description,
                start_utc=start_utc.isoformat(),
                end_utc=end_utc.isoformat(),
                category=categories,
                episode=episode
            )
            
        finally:
            # Clear element to free memory
            elem.clear()


def parse_xmltv_to_dict(filepath: Path = RAW_XMLTV_FILE) -> Dict[str, List[Programme]]:
    """
    Parse XMLTV file and group programmes by channel.
    Returns dict: {channel_id: [Programme, ...]}
    """
    if not filepath.exists():
        print(f"[ERROR] XMLTV file not found: {filepath}")
        return {}
    
    epg_data: Dict[str, List[Programme]] = {}
    count = 0
    
    for programme in stream_xml_programmes(filepath):
        if programme.channel_id not in epg_data:
            epg_data[programme.channel_id] = []
        epg_data[programme.channel_id].append(programme)
        count += 1
        
        if count % 10000 == 0:
            print(f"[PARSING] Processed {count} programmes...")
    
    # Sort programmes by start time for each channel
    for channel_id in epg_data:
        epg_data[channel_id].sort(key=lambda p: p.start_utc)
    
    print(f"[PARSED] {count} programmes for {len(epg_data)} channels")
    return epg_data


def save_epg(epg_data: Dict[str, List[Programme]], filepath: Path = EPG_DB_FILE):
    """Save EPG data to JSON file."""
    # Convert to serializable format
    output = {}
    for channel_id, programmes in epg_data.items():
        output[channel_id] = [p.to_dict() for p in programmes]
    
    with open(filepath, 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"[SAVED] EPG data to {filepath}")


def load_epg(filepath: Path = EPG_DB_FILE) -> Dict[str, List[dict]]:
    """Load EPG data from JSON file."""
    if not filepath.exists():
        return {}
    
    with open(filepath, 'r') as f:
        return json.load(f)


def get_programmes_for_channel(
    epg_data: Dict[str, List[dict]],
    channel_id: str,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None
) -> List[dict]:
    """
    Get programmes for a specific channel within a time range.
    Times should be in UTC.
    """
    if channel_id not in epg_data:
        return []
    
    programmes = epg_data[channel_id]
    result = []
    
    now = datetime.now(timezone.utc)
    start_time = start_time or now
    end_time = end_time or (start_time + timedelta(hours=2))
    
    start_str = start_time.isoformat()
    end_str = end_time.isoformat()
    
    for prog in programmes:
        # Check if programme overlaps with requested time range
        if prog['end_utc'] > start_str and prog['start_utc'] < end_str:
            result.append(prog)
    
    return result


async def process_epg():
    """Full pipeline: parse and save EPG data."""
    epg_data = parse_xmltv_to_dict()
    save_epg(epg_data)
    return epg_data


if __name__ == '__main__':
    epg_data = asyncio.run(process_epg())
    
    # Show sample
    if epg_data:
        first_channel = list(epg_data.keys())[0]
        print(f"\nSample programmes for channel '{first_channel}':")
        for prog in epg_data[first_channel][:3]:
            print(f"  {prog['start_utc']} - {prog['title']}")
