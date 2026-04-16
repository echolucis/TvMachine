"""
Phase 4: Channel-EPG Mapping & Normalization
Link M3U channels to XMLTV program data reliably.
"""
import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Set
from difflib import SequenceMatcher

CHANNELS_FILE = Path(__file__).parent / "data" / "channels.json"
EPG_FILE = Path(__file__).parent / "data" / "epg.json"
MAPPING_OVERRIDES_FILE = Path(__file__).parent / "data" / "mapping_overrides.json"
GUIDE_REGISTRY_FILE = Path(__file__).parent / "data" / "guide_registry.json"


def normalize_name(name: str) -> str:
    """
    Normalize channel name for fuzzy matching.
    - Lowercase
    - Strip punctuation
    - Remove common suffixes
    """
    # Lowercase
    name = name.lower()
    
    # Remove common suffixes
    suffixes = [' hd', ' uh', ' 4k', ' tv', ' channel', ' us', ' uk', ' international']
    for suffix in suffixes:
        if name.endswith(suffix):
            name = name[:-len(suffix)]
    
    # Strip punctuation and extra spaces
    name = re.sub(r'[^\w\s]', '', name)
    name = re.sub(r'\s+', ' ', name).strip()
    
    return name


def load_mapping_overrides() -> Dict[str, str]:
    """Load manual mapping overrides from file."""
    if not MAPPING_OVERRIDES_FILE.exists():
        return {}
    
    with open(MAPPING_OVERRIDES_FILE, 'r') as f:
        return json.load(f)


def save_mapping_overrides(overrides: Dict[str, str]):
    """Save mapping overrides to file."""
    with open(MAPPING_OVERRIDES_FILE, 'w') as f:
        json.dump(overrides, f, indent=2)


def fuzzy_match(query: str, candidates: Set[str], threshold: float = 0.8) -> Optional[str]:
    """
    Find best fuzzy match for query among candidates.
    Returns the best match if similarity > threshold, else None.
    """
    best_match = None
    best_score = 0.0
    
    for candidate in candidates:
        score = SequenceMatcher(None, query, candidate).ratio()
        if score > best_score and score >= threshold:
            best_score = score
            best_match = candidate
    
    return best_match


def resolve_channel(
    m3u_channel: dict,
    epg_channels: Set[str],
    overrides: Dict[str, str]
) -> Optional[str]:
    """
    Resolve M3U channel to EPG channel ID.
    
    Strategy:
    1. Check manual overrides
    2. Exact match on tvg-id
    3. Fuzzy match on normalized name
    
    Returns: EPG channel_id or None
    """
    # 1. Check overrides
    channel_name = m3u_channel.get('name', '')
    if channel_name in overrides:
        return overrides[channel_name]
    
    # 2. Exact match on tvg-id
    tvg_id = m3u_channel.get('tvg_id')
    if tvg_id and tvg_id in epg_channels:
        return tvg_id
    
    # 3. Fuzzy match on normalized name
    normalized = normalize_name(channel_name)
    match = fuzzy_match(normalized, epg_channels, threshold=0.7)
    
    if match:
        print(f"[MAPPED] '{channel_name}' -> '{match}' (fuzzy)")
        return match
    
    print(f"[UNMAPPED] No EPG match for '{channel_name}' (tvg_id: {tvg_id})")
    return None


def build_guide_registry(
    channels: List[dict],
    epg_data: Dict[str, List[dict]],
    overrides: Optional[Dict[str, str]] = None
) -> Dict[str, dict]:
    """
    Build unified guide registry linking channels to EPG data.
    
    Returns: {channel_id: {channel_info, epg_programmes}}
    """
    epg_channel_ids = set(epg_data.keys())
    overrides = overrides or {}
    
    registry = {}
    mapped_count = 0
    
    for channel in channels:
        channel_id = channel['id']
        
        # Try to resolve to EPG channel
        epg_channel_id = resolve_channel(channel, epg_channel_ids, overrides)
        
        registry[channel_id] = {
            'channel': channel,
            'epg_channel_id': epg_channel_id,
            'programmes': epg_data.get(epg_channel_id, []) if epg_channel_id else []
        }
        
        if epg_channel_id:
            mapped_count += 1
    
    coverage = (mapped_count / len(channels) * 100) if channels else 0
    print(f"[MAPPING] {mapped_count}/{len(channels)} channels mapped ({coverage:.1f}% coverage)")
    
    return registry


def load_channels(filepath: Path = CHANNELS_FILE) -> List[dict]:
    """Load channels from JSON file."""
    if not filepath.exists():
        return []
    
    with open(filepath, 'r') as f:
        return json.load(f)


def load_epg(filepath: Path = EPG_FILE) -> Dict[str, List[dict]]:
    """Load EPG data from JSON file."""
    if not filepath.exists():
        return {}
    
    with open(filepath, 'r') as f:
        return json.load(f)


def save_guide_registry(registry: Dict[str, dict], filepath: Path = GUIDE_REGISTRY_FILE):
    """Save guide registry to JSON file."""
    with open(filepath, 'w') as f:
        json.dump(registry, f, indent=2)
    
    print(f"[SAVED] Guide registry to {filepath}")


def create_sample_overrides():
    """Create a sample mapping overrides file."""
    sample_overrides = {
        "CNN HD": "cnn.us",
        "BBC One": "bbc1.uk",
        "Discovery Channel US": "discovery.us"
    }
    save_mapping_overrides(sample_overrides)
    print(f"[CREATED] Sample overrides at {MAPPING_OVERRIDES_FILE}")
    return sample_overrides


def process_mapping():
    """Full pipeline: load data, build registry, save results."""
    # Load data
    channels = load_channels()
    epg_data = load_epg()
    overrides = load_mapping_overrides()
    
    if not channels:
        print("[ERROR] No channels found. Run m3u_parser.py first.")
        return {}
    
    if not epg_data:
        print("[ERROR] No EPG data found. Run xmltv_parser.py first.")
        return {}
    
    # Build registry
    registry = build_guide_registry(channels, epg_data, overrides)
    
    # Save
    save_guide_registry(registry)
    
    return registry


if __name__ == '__main__':
    registry = process_mapping()
    
    # Show sample mappings
    if registry:
        print("\nSample mappings:")
        count = 0
        for ch_id, data in registry.items():
            if count >= 5:
                break
            channel_name = data['channel']['name']
            epg_id = data['epg_channel_id']
            prog_count = len(data['programmes'])
            print(f"  {channel_name} -> {epg_id} ({prog_count} programmes)")
            count += 1
