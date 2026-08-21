# AI News Aggregator v2

A modern AI-powered news aggregator with **Next.js frontend** and **FastAPI backend**. Fetches AI-related news from RSS feeds and YouTube, summarizes and categorizes items with an LLM, stores them in PostgreSQL, and sends personalized email digests.

## Features

- **Next.js 14 frontend** with App Router, Tailwind CSS, and responsive design
- **FastAPI backend** with automatic OpenAPI docs at `/docs`
- **User authentication**: JWT-based register/login with bcrypt password hashing
- **Admin dashboard**: manage users, sources, and trigger jobs
- **RSS & YouTube ingestion** from database-configured sources
- **AI-powered analysis**: OpenAI summarizes and categorizes every article
- **Personalized email digests** via Brevo (Jinja2 templates)
- **APScheduler** for daily aggregation at configurable hour
- **PostgreSQL** persistence with SQLAlchemy ORM
- **Docker** support for easy deployment

## Project Structure

```
ai-news-aggregator/
├── backend/                 # FastAPI + SQLAlchemy
│   ├── app/
│   │   ├── api/            # Routes, schemas, dependencies, security
│   │   ├── config/         # Settings management
│   │   ├── core/           # Pipeline orchestration
│   │   ├── data/           # Default source definitions
│   │   ├── email/          # Email sending & templates
│   │   ├── fetchers/       # RSS, YouTube fetchers
│   │   ├── models/         # SQLAlchemy models
│   │   ├── processors/     # AI content analysis
│   │   ├── scheduler/      # APScheduler integration
│   │   ├── services/       # Business logic layer
│   │   ├── storage/        # Database access (repository pattern)
│   │   └── utils/          # Helpers, errors, validators
│   ├── alembic/            # Database migrations
│   ├── scripts/            # CLI scripts
│   ├── tests/              # Pytest suite
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── render.yaml          # Render deployment config
├── frontend/               # Next.js 14 + Tailwind CSS
│   └── src/
│       ├── app/            # App Router pages
│       │   ├── page.tsx    # Landing page
│       │   ├── login/      # Login page
│       │   ├── register/   # Registration page
│       │   ├── news/       # News feed with search/filter
│       │   ├── settings/   # User settings & subscription
│       │   └── admin/      # Admin dashboard
│       ├── components/     # Reusable UI components
│       ├── context/        # Auth context provider
│       └── lib/            # API client & types
└── README.md
```

## Quick Start

### Option 1: Docker (Recommended)

```bash
cd backend
docker compose up --build
# Backend: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Option 2: Manual Setup

**Backend:**
```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env  # Edit with your values
docker compose up -d db  # Start PostgreSQL
python scripts/migrate_db.py
uvicorn app.api.main:app --reload
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
# http://localhost:3000
```

## API Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/v1/health` | No | Health check |
| POST | `/api/v1/auth/register` | No | Create account |
| POST | `/api/v1/auth/login` | No | Get JWT token |
| GET | `/api/v1/auth/me` | Yes | Get current user |
| PATCH | `/api/v1/auth/me/subscription` | Yes | Toggle digest subscription |
| GET | `/api/v1/sources` | No | List ingestion sources |
| POST | `/api/v1/sources` | Admin | Create source |
| PATCH | `/api/v1/sources/{id}` | Admin | Update source |
| DELETE | `/api/v1/sources/{id}` | Admin | Delete source |
| POST | `/api/v1/sources/sync-defaults` | Admin | Sync default sources |
| GET | `/api/v1/news` | No | List recent news |
| POST | `/api/v1/jobs/aggregate` | Admin | Trigger aggregation |
| GET | `/api/v1/admin/stats` | Admin | Dashboard statistics |
| GET | `/api/v1/admin/users` | Admin | List all users |

## Admin Access

- **Admin email**: `shivamadmin@mailinator.com` (configurable via `ADMIN_EMAIL` env var)
- **Admin routes**: Require `X-API-Key` header (set `API_KEY` in `.env`)
- **Admin dashboard**: Accessible at `/admin` in the frontend

## Configuration

```env
# Database
DATABASE_URL=postgresql://user:pass@localhost/ai_news

# JWT
JWT_SECRET_KEY=change-me-in-production

# OpenAI
OPENAI_API_KEY=sk-...

# Brevo
BREVO_ENABLED=true
BREVO_API_KEY=your-api-key
BREVO_SENDER_EMAIL=your-verified@email.com
BREVO_SENDER_NAME=AIPulse

# App
API_KEY=your-admin-key
ADMIN_EMAIL=shivamadmin@mailinator.com
CORS_ORIGINS=http://localhost:3000
SCHEDULER_ENABLED=true
CUSTOM_FETCH_HOUR=8
```

## Deployment

### Backend on Render

1. Connect your repo to Render
2. Use the `render.yaml` blueprint in `backend/`
3. Set environment variables in Render dashboard

### Frontend on Vercel

1. Import the `frontend` folder
2. Set `NEXT_PUBLIC_API_URL` to your backend URL
3. Deploy

## License

MIT
