# StreamFlix - Open Source IPTV & Plex Alternative

StreamFlix is a powerful, self-hosted media streaming platform that combines the best features of IPTV and Plex. It provides a unified interface for managing and streaming your media content, including movies, TV shows, and live TV channels.

## Features

- 🎬 **Movie & TV Show Streaming** - Browse and stream movies and TV episodes
- 📺 **Live TV Support** - Watch live TV channels with EPG support
- 🔍 **Smart Search** - Find content across multiple providers
- 👤 **User Management** - Multi-user support with personalized libraries
- 📱 **Multi-Platform** - Web, mobile, and smart TV apps
- 🎨 **Beautiful UI** - Modern, responsive interface
- ⚡ **High Performance** - Optimized for speed and reliability
- 🔒 **Privacy First** - Self-hosted, your data stays with you

## Architecture

```
streamflix/
├── backend/          # FastAPI-based backend server
│   ├── api/         # API endpoints
│   ├── core/        # Core business logic
│   ├── providers/   # Content providers (TMDB, torrent, etc.)
│   ├── models/      # Database models
│   └── routes/      # API routes
├── frontend/         # React/Next.js frontend application
│   ├── src/
│   │   ├── components/  # Reusable UI components
│   │   ├── pages/       # Application pages
│   │   ├── hooks/       # Custom React hooks
│   │   ├── services/    # API services
│   │   └── styles/      # CSS/Tailwind styles
│   └── public/      # Static assets
├── docker/          # Docker configuration
└── docs/            # Documentation
```

## Quick Start

### Prerequisites

- Docker & Docker Compose
- Node.js 18+ (for frontend development)
- Python 3.9+ (for backend development)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/your-org/streamflix.git
cd streamflix
```

2. **Configure environment variables**
```bash
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
```

3. **Start with Docker Compose**
```bash
docker-compose up -d
```

4. **Access the application**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## Configuration

### Environment Variables

#### Backend (.env)
```env
# Database
DATABASE_URL=postgresql://streamflix:password@db:5432/streamflix

# TMDB API
TMDB_API_KEY=your_tmdb_api_key

# JWT Secret
JWT_SECRET=your_secret_key

# Server
HOST=0.0.0.0
PORT=8000
```

#### Frontend (.env)
```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
NEXT_PUBLIC_APP_NAME=StreamFlix
```

## API Reference

The API follows RESTful conventions and supports:

- **Content Discovery**
  - `GET /api/v1/movies` - List movies
  - `GET /api/v1/tv` - List TV shows
  - `GET /api/v1/search?q=query` - Search content

- **Streaming**
  - `GET /api/v1/stream/movie/{id}` - Get movie streams
  - `GET /api/v1/stream/tv/{id}/{season}/{episode}` - Get episode streams

- **Live TV**
  - `GET /api/v1/channels` - List available channels
  - `GET /api/v1/epg/{channel_id}` - Get EPG for channel

- **User Management**
  - `POST /api/v1/auth/register` - Register user
  - `POST /api/v1/auth/login` - Login
  - `GET /api/v1/user/library` - Get user library

For complete API documentation, visit `/docs` after starting the server.

## Development

### Backend Development

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend Development

```bash
cd frontend
npm install
npm run dev
```

## Providers

StreamFlix supports multiple content providers:

- **TMDB** - Metadata for movies and TV shows
- **Torrent Providers** - For streaming sources
- **IPTV Providers** - Live TV channels (M3U playlists)
- **Custom Sources** - Add your own media files

## Roadmap

- [ ] Torrent streaming integration
- [ ] Live DVR functionality
- [ ] Mobile apps (iOS/Android)
- [ ] Smart TV apps
- [ ] Subtitle support
- [ ] Watch party feature
- [ ] AI-powered recommendations

## Contributing

We welcome contributions! Please see our [Contributing Guide](docs/CONTRIBUTING.md) for details.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Inspired by projects like Jellyfin, Plex, and Stremio
- Uses TMDB for metadata
- Built with modern web technologies

---

**Note**: This software is for educational purposes. Users are responsible for ensuring they have the right to access and stream the content they view through this application.
