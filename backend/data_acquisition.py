"""
Phase 1: Data Acquisition & Local Storage
Fetch, validate, and store raw M3U and XMLTV files efficiently.
"""
import aiohttp
import asyncio
import hashlib
import json
import os
from datetime import datetime
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"
RAW_M3U_DIR = DATA_DIR / "raw" / "m3u"
RAW_XMLTV_DIR = DATA_DIR / "raw" / "xmltv"

# Default sources (iptv-org)
DEFAULT_M3U_URL = "https://iptv-org.github.io/iptv/index.m3u"
DEFAULT_XMLTV_URL = "https://iptv-org.github.io/epg/guide.xml"


def compute_hash(content: bytes) -> str:
    """Compute SHA256 hash of content."""
    return hashlib.sha256(content).hexdigest()


async def fetch_with_cache(
    session: aiohttp.ClientSession,
    url: str,
    cache_dir: Path,
    filename: str,
) -> dict:
    """
    Fetch URL with ETag/Last-Modified caching.
    Returns metadata about the fetch operation.
    """
    cache_file = cache_dir / filename
    meta_file = cache_dir / f"{filename}.meta"
    
    headers = {}
    
    # Load existing metadata for conditional requests
    if meta_file.exists():
        with open(meta_file, 'r') as f:
            meta = json.load(f)
            if 'etag' in meta:
                headers['If-None-Match'] = meta['etag']
            if 'last_modified' in meta:
                headers['If-Modified-Since'] = meta['last_modified']
    
    # Retry logic with exponential backoff
    max_retries = 3
    for attempt in range(max_retries):
        try:
            async with session.get(url, headers=headers, timeout=30) as response:
                if response.status == 304:
                    # Not modified, use cached version
                    print(f"[CACHE] {url} - Not modified")
                    return {
                        'status': 'cached',
                        'source_url': url,
                        'cached_at': meta.get('downloaded_at') if meta_file.exists() else None,
                        'hash': meta.get('hash'),
                    }
                
                if response.status == 200:
                    content = await response.read()
                    
                    # Save raw content
                    cache_file.write_bytes(content)
                    
                    # Save metadata
                    new_meta = {
                        'downloaded_at': datetime.utcnow().isoformat(),
                        'hash': compute_hash(content),
                        'source_url': url,
                        'size': len(content),
                        'etag': response.headers.get('ETag'),
                        'last_modified': response.headers.get('Last-Modified'),
                    }
                    with open(meta_file, 'w') as f:
                        json.dump(new_meta, f, indent=2)
                    
                    print(f"[FETCHED] {url} - {len(content)} bytes")
                    return {
                        'status': 'fetched',
                        **new_meta
                    }
                
                print(f"[ERROR] {url} - Status: {response.status}")
                return {'status': 'error', 'code': response.status}
                
        except (aiohttp.ClientError, asyncio.TimeoutError) as e:
            if attempt == max_retries - 1:
                print(f"[ERROR] {url} - Failed after {max_retries} attempts: {e}")
                return {'status': 'error', 'message': str(e)}
            wait_time = 2 ** attempt
            print(f"[RETRY] {url} - Waiting {wait_time}s before retry {attempt + 1}/{max_retries}")
            await asyncio.sleep(wait_time)
    
    return {'status': 'error', 'message': 'Max retries exceeded'}


async def acquire_data(m3u_url: str = DEFAULT_M3U_URL, xmltv_url: str = DEFAULT_XMLTV_URL):
    """Acquire both M3U and XMLTV data."""
    # Ensure directories exist
    RAW_M3U_DIR.mkdir(parents=True, exist_ok=True)
    RAW_XMLTV_DIR.mkdir(parents=True, exist_ok=True)
    
    async with aiohttp.ClientSession() as session:
        tasks = [
            fetch_with_cache(session, m3u_url, RAW_M3U_DIR, 'playlist.m3u'),
            fetch_with_cache(session, xmltv_url, RAW_XMLTV_DIR, 'guide.xml'),
        ]
        results = await asyncio.gather(*tasks)
    
    return {
        'm3u': results[0],
        'xmltv': results[1],
    }


if __name__ == '__main__':
    result = asyncio.run(acquire_data())
    print(json.dumps(result, indent=2))
