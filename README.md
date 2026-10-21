# AI Pulse

A full-stack, AI-powered news aggregation platform that fetches, analyzes, and delivers personalized AI news digests. Built with **Vite + React** on the frontend and **FastAPI** on the backend, powered by LLMs for summarization and categorization.

![Vite](https://img.shields.io/badge/Vite-5-646CFF?logo=vite&logoColor=white)
![React](https://img.shields.io/badge/React-18-61DAFB?logo=react&logoColor=black)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-teal?logo=fastapi)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?logo=postgresql)
![Docker](https://img.shields.io/badge-Docker-2496ED?logo=docker)
![License](https://img.shields.io/badge/License-MIT-green)

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [API Reference](#api-reference)
- [Deployment](#deployment)
- [Testing](#testing)
- [Contributing](#contributing)
- [License](#license)

## Overview

AI Pulse continuously monitors RSS feeds, YouTube channels, Medium publications, and web sources for the latest in artificial intelligence. Every article is summarized, relevance-scored, and categorized by an LLM before being stored in PostgreSQL. Users subscribe to personalized email digests on their preferred schedule — daily, weekly, or instant.

The platform includes a full admin dashboard for managing users, ingestion sources, and triggering aggregation jobs, plus JWT-based authentication with role-based access control.

## Features

### Core
- **Multi-source ingestion** — RSS, YouTube, Medium, and web scraping from database-configured sources
- **AI-powered analysis** — LLM summarization, categorization, and relevance scoring for every article
- **Personalized email digests** — Jinja2-templated emails delivered on a configurable schedule
- **User authentication** — JWT-based register/login with bcrypt password hashing
- **Role-based access** — Admin vs. regular user permissions with API key protection

### Frontend
- **Vite + React 18 SPA** with React Router — every route code-split, error boundary + retrying lazy loads
- **Tailwind CSS** design system: gradient washes, scroll-reveal animation, glass surfaces (respects `prefers-reduced-motion`)
- **News feed** with search, category filtering, and pagination
- **User settings** — subscription management, digest frequency preferences
- **Admin dashboard** — user management, source management, job triggers, statistics
- **Toast notifications** and skeleton loading states
- **Errors surface in-app** — API failures render inline/toast messages; an expired session moves you to sign-in with an explanation instead of reloading the page

### Backend
- **FastAPI** with automatic OpenAPI docs at `/docs`
- **SQLAlchemy ORM** with repository pattern for data access
- **Alembic** database migrations
- **APScheduler** for automated daily aggregation
- **PostgreSQL** persistence with Redis caching layer
- **Docker** support for containerized deployment

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Vite 5, React 18, React Router 6, Tailwind CSS, TypeScript |
| Backend | FastAPI, Python 3.11+, SQLAlchemy, Pydantic |
| Database | PostgreSQL, Redis (caching) |
| AI | OpenAI API (GPT-4o-mini for summarization) |
| Auth | JWT (python-jose), bcrypt |
| Email | Brevo API, Jinja2 templates |
| Scheduling | APScheduler |
| Deployment | Docker, Render (backend), Vercel or nginx (frontend) |

## Project Structure

```
ai-news-aggregater/
├── backend/                 # FastAPI + SQLAlchemy
│   ├── app/
│   │   ├── api/            # Routes, schemas, dependencies, security
│   │   ├── config/         # Settings management
│   │   ├── core/           # Pipeline orchestration
│   │   ├── data/           # Default source definitions
│   │   ├── email/          # Email sending & templates
│   │   ├── fetchers/       # RSS, YouTube, web fetchers
│   │   ├── models/         # SQLAlchemy models
│   │   ├── processors/     # AI content analysis
│   │   ├── scheduler/      # APScheduler integration
│   │   ├── services/       # Business logic layer
│   │   ├── storage/        # Database access (repository pattern)
│   │   └── utils/          # Helpers, errors, validators
│   ├── alembic/            # Database migrations
│   ├── scripts/            # CLI scripts (migrate, seed, run)
│   ├── tests/              # Pytest suite
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── render.yaml          # Render deployment config
├── frontend/               # Vite + React SPA (Tailwind CSS)
│   ├── index.html          # SPA entry point
│   ├── vite.config.ts      # `@` alias, dev server on :3000, /api proxy
│   ├── nginx.conf          # SPA fallback + optional API reverse proxy
│   └── src/
│       ├── pages/          # Home, Login, Register, News, Settings, Admin
│       ├── components/     # Navbar, AuthLayout, ErrorBoundary, ui/, admin/
│       ├── context/        # Auth context provider
│       ├── shared/         # API client, error normalization, helpers
│       ├── styles/         # globals.css — design tokens & component classes
│       └── App.tsx         # Router, lazy routes, session-expiry watcher
└── README.md
```

## Quick Start

### Prerequisites

- Node.js 18+ and npm
- Python 3.11+
- PostgreSQL 15+
- Docker (optional but recommended)

### Option 1: Docker (Recommended)

```bash
# Start backend + database
cd backend
docker compose up --build

# Backend: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

In a separate terminal:

```bash
cd frontend
npm install
npm run dev
# Frontend: http://localhost:3000 (Vite dev server, /api proxied to the backend)
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
npm run dev      # http://localhost:3000
npm run preview  # serve the production build from dist/ on :4173
```

## Configuration

Create a `.env` file in the `backend/` directory:

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
# Must list the frontend origin(s), or the browser blocks every API call with
# a CORS error (axios then reports a bare "Network Error").
CORS_ORIGINS=http://localhost:3000
SCHEDULER_ENABLED=true
CUSTOM_FETCH_HOUR=8

# GitHub trending AI repositories (fetched daily as part of the aggregation run)
# Optional personal access token raises the search rate limit (30/min vs 10/min).
GITHUB_TOKEN=
# Comma-separated topics for the trending search (default shown).
GITHUB_AI_TOPICS=ai,llm,machine-learning,deep-learning,agents
# Max repos stored per run / only repos created in the last N days count as trending.
AGGREGATION_GITHUB_LIMIT=5
AGGREGATION_GITHUB_LOOKBACK_DAYS=7
```

For the frontend, set these in `frontend/.env`:

```env
# Absolute backend URL the browser calls (no trailing slash).
# Falls back to http://localhost:8000 when unset.
VITE_API_URL=http://localhost:8000

# Where the Vite dev server proxies relative /api/* requests to.
VITE_PROXY_TARGET=http://localhost:8000
```

## API Reference

Full interactive API documentation is available at `/docs` when the backend is running.

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/v1/health` | No | Health check |
| POST | `/api/v1/register` | No | Create account |
| POST | `/api/v1/login` | No | Get JWT token |
| POST | `/api/v1/refresh` | No | Rotate an expired token pair |
| GET | `/api/v1/me` | Yes | Get current user |
| PATCH | `/api/v1/me/subscription` | Yes | Toggle digest subscription |
| POST | `/api/v1/me/change-password` | Yes | Change password |
| GET | `/api/v1/sources` | No | List ingestion sources |
| POST | `/api/v1/sources` | Admin | Create source |
| PATCH | `/api/v1/sources/{id}` | Admin | Update source |
| DELETE | `/api/v1/sources/{id}` | Admin | Delete source |
| POST | `/api/v1/sources/sync-defaults` | Admin | Sync default sources |
| GET | `/api/v1/news` | No | List recent news |
| POST | `/api/v1/jobs/aggregate` | Admin | Trigger aggregation |
| GET | `/api/v1/admin/stats` | Admin | Dashboard statistics |
| GET | `/api/v1/admin/users` | Admin | List all users |

## Deployment

### Backend on Render

1. Connect your repository to Render
2. Use the `render.yaml` blueprint in `backend/`
3. Set environment variables in the Render dashboard

### Frontend

The frontend builds to static files (`dist`), so any static host works.

**Vercel** — `frontend/vercel.json` already declares the Vite build command,
output directory, and the SPA rewrite that keeps deep links like `/news`
working after a reload:

1. Import the `frontend` folder into Vercel
2. Set `VITE_API_URL` to your backend URL (build-time variable), e.g. `https://your-api.onrender.com`
3. Deploy — and add that Vercel origin to `CORS_ORIGINS` on the backend

**Docker + nginx** — `frontend/Dockerfile` builds the SPA and serves it from
nginx on port 3000, with `BACKEND_URL` substituted into `nginx.conf` at
startup for the optional `/api/` reverse proxy:

```bash
docker build -t ai-pulse-frontend frontend
docker run -p 3000:3000 -e BACKEND_URL=http://localhost:8000 ai-pulse-frontend
```

## Testing

```bash
# Backend tests
cd backend
pytest tests/ -v

# Frontend — typecheck (tsc --noEmit) + production build
cd frontend
npm run build
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
