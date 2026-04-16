"""
Phase 2: M3U Playlist Parser
Convert raw M3U text into a structured channel list.
"""
import re
import asyncio
import aiohttp
from pathlib import Path
from typing import Optional, List, Dict
from dataclasses import dataclass, asdict

RAW_M3U_FILE = Path(__file__).parent / "data" / "raw" / "m3u" / "playlist.m3u"
CHANNELS_FILE = Path(__file__).parent / "data" / "channels.json"


@dataclass
class Channel:
    id: str
    name: str
    logo: Optional[str]
    group: Optional[str]
    tvg_id: Optional[str]
    url: str
    status: str = "unknown"
    
    def to_dict(self) -> dict:
        return asdict(self)


def parse_m3u_attributes(line: str) -> dict:
    """Extract key-value pairs from #EXTINF line."""
    attrs = {}
    # Match patterns like: tvg-id="cnn.us" or tvg-logo="http://..."
    pattern = r'(\w+(?:-\w+)*)="([^"]*)"'
    matches = re.findall(pattern, line)
    for key, value in matches:
        attrs[key] = value
    return attrs


def generate_channel_id(name: str, url: str) -> str:
    """Generate a unique channel ID from name and URL."""
    import hashlib
    combined = f"{name}:{url}".lower()
    return hashlib.md5(combined.encode()).hexdigest()[:12]


def parse_m3u(content: str) -> List[Channel]:
    """Parse M3U content into list of Channel objects."""
    channels = []
    lines = content.strip().split('\n')
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        if line.startswith('#EXTINF:'):
            # Extract attributes
            attrs = parse_m3u_attributes(line)
            
            # Extract display name (after last comma)
            name_match = re.search(r',([^,]+)$', line)
            name = name_match.group(1).strip() if name_match else "Unknown"
            
            # Next line should be the URL
            url = ""
            if i + 1 < len(lines):
                url = lines[i + 1].strip()
                if url.startswith('#'):
                    url = ""  # Skip comments
                i += 1
            
            if url:
                channel = Channel(
                    id=generate_channel_id(name, url),
                    name=name,
                    logo=attrs.get('tvg-logo'),
                    group=attrs.get('group-title'),
                    tvg_id=attrs.get('tvg-id'),
                    url=url,
                    status="unknown"
                )
                channels.append(channel)
        
        i += 1
    
    return channels


async def validate_channel(session: aiohttp.ClientSession, channel: Channel, timeout: int = 5) -> Channel:
    """Validate channel URL with HEAD request."""
    try:
        async with session.head(channel.url, timeout=timeout, allow_redirects=True) as response:
            if response.status in (200, 302, 301):
                channel.status = "active"
            else:
                channel.status = "dead"
    except (aiohttp.ClientError, asyncio.TimeoutError):
        channel.status = "dead"
    
    return channel


async def validate_channels(channels: List[Channel], max_concurrent: int = 20) -> List[Channel]:
    """Validate all channels concurrently with limited concurrency."""
    async with aiohttp.ClientSession() as session:
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def bounded_validate(channel: Channel) -> Channel:
            async with semaphore:
                return await validate_channel(session, channel)
        
        tasks = [bounded_validate(ch) for ch in channels]
        results = await asyncio.gather(*tasks)
        
        # Count results
        active = sum(1 for ch in results if ch.status == "active")
        dead = sum(1 for ch in results if ch.status == "dead")
        print(f"[VALIDATION] Active: {active}, Dead: {dead}, Total: {len(results)}")
        
        return list(results)


def load_and_parse_m3u(filepath: Path = RAW_M3U_FILE) -> List[Channel]:
    """Load M3U file and parse it."""
    if not filepath.exists():
        print(f"[ERROR] M3U file not found: {filepath}")
        return []
    
    content = filepath.read_text(encoding='utf-8')
    channels = parse_m3u(content)
    print(f"[PARSED] {len(channels)} channels from M3U")
    return channels


async def process_channels(validate: bool = True) -> List[Channel]:
    """Full pipeline: load, parse, and optionally validate channels."""
    channels = load_and_parse_m3u()
    
    if validate and channels:
        channels = await validate_channels(channels)
    
    # Save to JSON
    data = [ch.to_dict() for ch in channels]
    with open(CHANNELS_FILE, 'w') as f:
        import json
        json.dump(data, f, indent=2)
    
    print(f"[SAVED] {len(channels)} channels to {CHANNELS_FILE}")
    return channels


if __name__ == '__main__':
    channels = asyncio.run(process_channels(validate=False))
    print(f"First 5 channels:")
    for ch in channels[:5]:
        print(f"  - {ch.name} ({ch.tvg_id})")
