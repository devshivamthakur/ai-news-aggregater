# AI News Aggregator

A full-stack, AI-powered news aggregation platform that fetches, analyzes, and delivers personalized AI news digests. Built with **Next.js 14** on the frontend and **FastAPI** on the backend, powered by LLMs for summarization and categorization.

![Next.js](https://img.shields.io/badge/Next.js-14-black?logo=nextdotjs)
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

AI News Aggregator continuously monitors RSS feeds, YouTube channels, Medium publications, and web sources for the latest in artificial intelligence. Every article is summarized, relevance-scored, and categorized by an LLM before being stored in PostgreSQL. Users subscribe to personalized email digests on their preferred schedule — daily, weekly, or instant.

The platform includes a full admin dashboard for managing users, ingestion sources, and triggering aggregation jobs, plus JWT-based authentication with role-based access control.

## Features

### Core
- **Multi-source ingestion** — RSS, YouTube, Medium, and web scraping from database-configured sources
- **AI-powered analysis** — LLM summarization, categorization, and relevance scoring for every article
- **Personalized email digests** — Jinja2-templated emails delivered on a configurable schedule
- **User authentication** — JWT-based register/login with bcrypt password hashing
- **Role-based access** — Admin vs. regular user permissions with API key protection

### Frontend
- **Next.js 14** App Router with server and client components
- **Tailwind CSS** for responsive, modern UI
- **News feed** with search, category filtering, and infinite scroll
- **User settings** — subscription management, digest frequency preferences
- **Admin dashboard** — user management, source management, job triggers, statistics
- **Toast notifications** and skeleton loading states

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
| Frontend | Next.js 14, React 18, Tailwind CSS, TypeScript |
| Backend | FastAPI, Python 3.11+, SQLAlchemy, Pydantic |
| Database | PostgreSQL, Redis (caching) |
| AI | OpenAI API (GPT-4o-mini for summarization) |
| Auth | JWT (python-jose), bcrypt |
| Email | aiosmtplib, Jinja2 templates |
| Scheduling | APScheduler |
| Deployment | Docker, Render (backend), Vercel (frontend) |

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
│       └── lib/            # API client & utilities
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
# Frontend: http://localhost:3000
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

# SMTP
SMTP_SERVER=smtp.gmail.com
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# App
API_KEY=your-admin-key
ADMIN_EMAIL=shivamadmin@mailinator.com
CORS_ORIGINS=http://localhost:3000
SCHEDULER_ENABLED=true
CUSTOM_FETCH_HOUR=8
```

For the frontend, set `NEXT_PUBLIC_API_URL` to your backend URL (defaults to `http://localhost:8000`).

## API Reference

Full interactive API documentation is available at `/docs` when the backend is running.

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

## Deployment

### Backend on Render

1. Connect your repository to Render
2. Use the `render.yaml` blueprint in `backend/`
3. Set environment variables in the Render dashboard

### Frontend on Vercel

1. Import the `frontend` folder into Vercel
2. Set `NEXT_PUBLIC_API_URL` to your backend URL
3. Deploy

## Testing

```bash
# Backend tests
cd backend
pytest tests/ -v

# Frontend lint
cd frontend
npm run lint
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
