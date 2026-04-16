# Pipeline Runner
# Runs all data processing phases in sequence

import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from data_acquisition import acquire_data
from m3u_parser import process_channels
from xmltv_parser import process_epg
from mapping_engine import process_mapping


async def run_pipeline(m3u_url: str = None, xmltv_url: str = None, validate_streams: bool = False):
    """
    Run the complete data processing pipeline.
    
    Args:
        m3u_url: Custom M3U URL (default: iptv-org index)
        xmltv_url: Custom XMLTV URL (default: iptv-org guide)
        validate_streams: Whether to validate stream URLs (slow but recommended)
    """
    print("=" * 60)
    print("IPTV/EPG Data Processing Pipeline")
    print("=" * 60)
    
    # Phase 1: Data Acquisition
    print("\n[PHASE 1] Acquiring data...")
    fetch_result = await acquire_data(m3u_url, xmltv_url)
    
    if fetch_result['m3u'].get('status') == 'error':
        print("❌ Failed to fetch M3U playlist")
        return False
    
    if fetch_result['xmltv'].get('status') == 'error':
        print("⚠️  Failed to fetch XMLTV guide (continuing without EPG)")
    
    # Phase 2: M3U Parsing
    print("\n[PHASE 2] Parsing M3U playlist...")
    channels = await process_channels(validate=validate_streams)
    
    if not channels:
        print("❌ No channels parsed")
        return False
    
    # Phase 3: XMLTV Parsing
    print("\n[PHASE 3] Parsing XMLTV guide...")
    epg_data = await process_epg()
    
    if not epg_data:
        print("⚠️  No EPG data parsed")
    
    # Phase 4: Channel-EPG Mapping
    print("\n[PHASE 4] Building channel-EPG mappings...")
    registry = process_mapping()
    
    if not registry:
        print("⚠️  Failed to build registry")
    
    # Summary
    print("\n" + "=" * 60)
    print("Pipeline Complete!")
    print("=" * 60)
    print(f"✓ Channels: {len(channels)}")
    print(f"✓ EPG Channels: {len(epg_data)}")
    print(f"✓ Mapped Channels: {len(registry)}")
    print(f"\nData files saved to: {Path(__file__).parent / 'data'}")
    print("\nNext steps:")
    print("  1. Run: python main.py (to start API server)")
    print("  2. Open frontend in browser")
    
    return True


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='IPTV/EPG Data Pipeline')
    parser.add_argument('--m3u', help='Custom M3U URL')
    parser.add_argument('--xmltv', help='Custom XMLTV URL')
    parser.add_argument('--validate', action='store_true', help='Validate stream URLs')
    
    args = parser.parse_args()
    
    success = asyncio.run(run_pipeline(
        m3u_url=args.m3u,
        xmltv_url=args.xmltv,
        validate_streams=args.validate
    ))
    
    sys.exit(0 if success else 1)
