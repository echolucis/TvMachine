import httpx
import re
from typing import List, Dict, Any
from urllib.parse import urlparse


class IPTVProvider:
    """IPTV M3U playlist parser and EPG provider."""
    
    def __init__(self):
        self.timeout = 15.0
    
    async def parse_m3u(self, url: str) -> List[Dict[str, Any]]:
        """Parse M3U playlist from URL."""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(url)
            response.raise_for_status()
            content = response.text
        
        return self._parse_m3u_content(content)
    
    def _parse_m3u_content(self, content: str) -> List[Dict[str, Any]]:
        """Parse M3U content string."""
        channels = []
        lines = content.strip().split('\n')
        
        if not lines or not lines[0].startswith('#EXTM3U'):
            raise ValueError("Invalid M3U format - missing #EXTM3U header")
        
        current_channel = {}
        
        for line in lines[1:]:
            line = line.strip()
            
            if not line:
                continue
            
            if line.startswith('#EXTINF:'):
                # Parse EXTINF line
                # Format: #EXTINF:-1 tvg-id="BBC1" tvg-name="BBC One" tvg-logo="http://..." group-title="News",BBC One
                current_channel = self._parse_extinf(line)
            
            elif line.startswith('#'):
                # Other metadata lines (catchup, timeshift, etc.)
                self._parse_metadata(line, current_channel)
            
            else:
                # This is the stream URL
                if current_channel:
                    current_channel['stream_url'] = line
                    current_channel['is_active'] = True
                    channels.append(current_channel)
                    current_channel = {}
        
        return channels
    
    def _parse_extinf(self, line: str) -> Dict[str, Any]:
        """Parse EXTINF line."""
        channel = {
            'name': '',
            'logo': None,
            'group': None,
            'country': None,
            'language': None,
            'epg_id': None,
        }
        
        # Extract channel name (after the last comma)
        parts = line.split(',')
        if len(parts) > 1:
            channel['name'] = parts[-1].strip()
        
        # Extract metadata attributes
        # tvg-id
        tvg_id_match = re.search(r'tvg-id="([^"]*)"', line)
        if tvg_id_match:
            channel['epg_id'] = tvg_id_match.group(1)
        
        # tvg-logo
        tvg_logo_match = re.search(r'tvg-logo="([^"]*)"', line)
        if tvg_logo_match:
            channel['logo'] = tvg_logo_match.group(1)
        
        # group-title
        group_match = re.search(r'group-title="([^"]*)"', line)
        if group_match:
            channel['group'] = group_match.group(1)
        
        # tvg-country
        country_match = re.search(r'tvg-country="([^"]*)"', line)
        if country_match:
            channel['country'] = country_match.group(1)
        
        # tvg-language
        language_match = re.search(r'tvg-language="([^"]*)"', line)
        if language_match:
            channel['language'] = language_match.group(1)
        
        return channel
    
    def _parse_metadata(self, line: str, channel: Dict[str, Any]):
        """Parse other metadata lines."""
        # Catchup days
        catchup_days_match = re.search(r'catchup-days="(\d+)"', line)
        if catchup_days_match:
            channel['catchup_days'] = int(catchup_days_match.group(1))
        
        # Catchup type
        catchup_type_match = re.search(r'catchup-type="([^"]*)"', line)
        if catchup_type_match:
            channel['catchup_type'] = catchup_type_match.group(1)
        
        # Timeshift
        timeshift_match = re.search(r'timeshift="([^"]*)"', line)
        if timeshift_match:
            channel['timeshift'] = timeshift_match.group(1)
    
    async def get_epg(self, epg_id: str, days: int = 1) -> Dict[str, Any]:
        """Get EPG data for a channel."""
        # TODO: Implement actual EPG fetching from XMLTV or other sources
        # For now, return mock data
        return {
            "channel_id": epg_id,
            "days": days,
            "programs": [
                {
                    "title": "Sample Program",
                    "start": "2024-01-01T00:00:00Z",
                    "end": "2024-01-01T01:00:00Z",
                    "description": "This is a sample program",
                    "icon": None,
                }
            ]
        }
    
    async def validate_stream(self, stream_url: str) -> bool:
        """Validate if a stream URL is accessible."""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.head(stream_url)
                return response.status_code < 400
        except Exception:
            return False
