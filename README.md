# IPTV/EPG System

A complete IPTV/EPG system with Python backend and JavaScript frontend, implementing the full roadmap from data acquisition to playback.

## Architecture

```
[Raw M3U/XMLTV] → [Parsers] → [Mapping Engine] → [FastAPI Backend] → [Vanilla JS Frontend]
```

## Quick Start

### Windows (One-Click)
Simply double-click **`launch.bat`** in the root directory. The script will:
1. Check for Python and Node.js installations
2. Create a virtual environment and install dependencies
3. Run the data pipeline to fetch M3U/XMLTV
4. Open two windows: Backend API and Frontend UI

Access:
- **Backend API**: http://localhost:8000
- **Frontend UI**: http://localhost:5173
- **API Docs**: http://localhost:8000/docs

### Linux/Mac (One-Click)
```bash
./launch.sh
```

### Manual Start

#### 1. Install Backend Dependencies
```bash
cd backend
pip install -r requirements.txt
```

#### 2. Run Data Pipeline
Fetch and process IPTV data:
```bash
python run_pipeline.py
```

Optional flags:
- `--validate` - Validate stream URLs (slower but recommended)
- `--m3u URL` - Custom M3U playlist URL
- `--xmltv URL` - Custom XMLTV guide URL

#### 3. Start API Server
```bash
python main.py
```
Server runs at: http://localhost:8000

#### 4. Install & Run Frontend
```bash
cd frontend
npm install
npm run dev
```
Frontend runs at: http://localhost:5173

## Project Structure

```
.
├── backend/
│   ├── data_acquisition.py    # Phase 1: Fetch M3U/XMLTV
│   ├── m3u_parser.py          # Phase 2: Parse channels
│   ├── xmltv_parser.py        # Phase 3: Parse EPG
│   ├── mapping_engine.py      # Phase 4: Channel-EPG mapping
│   ├── main.py                # Phase 5&6: FastAPI server
│   ├── run_pipeline.py        # Complete pipeline runner
│   └── data/                  # Generated data files
│       ├── raw/               # Raw M3U/XMLTV files
│       ├── channels.json      # Parsed channels
│       ├── epg.json           # Parsed EPG
│       └── guide_registry.json # Unified guide
└── frontend/
    ├── index.html             # Main HTML
    ├── src/main.js            # Frontend application
    └── package.json
```

## API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /api/health` | System health and stats |
| `GET /api/channels` | List all channels |
| `GET /api/channel/{id}` | Channel details with current programme |
| `GET /api/guide?channel_id=&start=&end=` | EPG for time range |
| `GET /api/search?q=` | Search programmes |
| `GET /api/stream/{id}` | Redirect to stream URL |
| `GET /api/groups` | List channel groups |

## Features

### Backend (Python)
- ✅ HTTP caching with ETag/Last-Modified
- ✅ Async M3U parsing with regex
- ✅ Streaming XMLTV parser (memory efficient)
- ✅ Fuzzy channel name matching
- ✅ Manual mapping overrides
- ✅ FastAPI REST API with CORS
- ✅ Time-aware EPG queries
- ✅ Full-text search across programmes

### Frontend (JavaScript)
- ✅ Responsive 3-column layout
- ✅ Channel list with status indicators
- ✅ EPG timeline view
- ✅ HLS.js video player
- ✅ Debounced search with results
- ✅ Keyboard navigation (↑/↓)
- ✅ Auto-play support
- ✅ Dark theme UI

## Configuration

### Custom Data Sources

Edit `data_acquisition.py` or use CLI flags:

```bash
python run_pipeline.py --m3u "https://example.com/playlist.m3u" --xmltv "https://example.com/guide.xml"
```

### Manual Channel Mapping

Create/edit `backend/data/mapping_overrides.json`:

```json
{
  "CNN HD": "cnn.us",
  "BBC One": "bbc1.uk"
}
```

## Development

### Run Individual Phases

```bash
# Just fetch data
python data_acquisition.py

# Just parse M3U
python m3u_parser.py

# Just parse EPG
python xmltv_parser.py

# Just build mappings
python mapping_engine.py
```

### API Documentation

Once server is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Troubleshooting

**No channels loaded:**
- Check if `run_pipeline.py` completed successfully
- Verify `backend/data/channels.json` exists

**Backend offline error:**
- Ensure `python main.py` is running
- Check port 8000 is not in use

**Streams not playing:**
- Some streams may be geo-restricted or dead
- Run pipeline with `--validate` to filter dead streams
- Check browser console for CORS errors

**EPG not showing:**
- Verify `backend/data/epg.json` was created
- Check channel mapping in `guide_registry.json`

## Next Steps

1. **Automation**: Add cron job for `run_pipeline.py`
2. **Database**: Switch from JSON to SQLite for scale
3. **Authentication**: Add user auth for remote access
4. **Docker**: Containerize for easy deployment
5. **Proxy**: Add stream proxy for ad-blocking/header injection

## License

MIT
