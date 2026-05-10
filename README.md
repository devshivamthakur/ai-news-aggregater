# AI News Aggregator

Fetches AI-related news from RSS feeds and YouTube, summarizes and categorizes items with an LLM, stores them in PostgreSQL, and sends personalized email digests based on user interests. Scheduling is driven by environment variables (hourly window and optional daily job).

## Features

- **FastAPI** service with health, sources, news, and job triggers (`/docs` OpenAPI)
- RSS and YouTube ingestion from **`ingestion_sources` table** (no feed URLs in application code)
- One-shot **sync** of bundled defaults into Postgres (`ai_news_aggregater/data/default_sources.py`)
- **APScheduler** inside the API process: daily aggregation at `CUSTOM_FETCH_HOUR` (timezone-aware)
- OpenAI-powered titles, summaries, and categories
- PostgreSQL persistence with fetch metadata
- SMTP email digests (Jinja2 templates)
- Configurable fetch timeouts, retries, and aggregation window

## Requirements

- **Python** 3.14+ (see `pyproject.toml`)
- **PostgreSQL** for production; Docker Compose provides a local database
- **OpenAI** API key (and optional `OPENAI_BASE_URL` for compatible endpoints)

## Quick start

### 1. Install

Using [uv](https://docs.astral.sh/uv/) (recommended; `uv.lock` is committed):

```bash
uv sync
```

Or pip:

```bash
pip install -e .
```

### 2. Environment

Copy the example file and fill in values:

```bash
cp .env.example .env
```

See **Configuration** below for important variables.

### 3. Database

Start Postgres locally (optional):

```bash
docker compose up -d db
```

Create tables (SQLAlchemy `create_all`):

```bash
uv run python scripts/migrate_db.py
```

Or apply Alembic migrations:

```bash
uv run python scripts/run_migrations.py
```

### 4. Seed ingestion sources

RSS URLs and YouTube channel IDs live in the database. After migrations / `create_tables`, either:

- Set `SYNC_DEFAULT_SOURCES_ON_STARTUP=true` (see `.env.example`), or
- Call the API once you are running the server (see below): `POST /api/v1/sources/sync-defaults` with `X-API-Key` if `API_KEY` is set.

Defaults to upsert are defined only in `ai_news_aggregater/data/default_sources.py` (used by the sync service, not at fetch time).

### 5. Run

**HTTP API (recommended for production)** — serves OpenAPI at `/docs`, runs the scheduler in-process when `SCHEDULER_ENABLED=true`:

```bash
uv run uvicorn ai_news_aggregater.api.main:app --host 0.0.0.0 --port 8000
```

**One-shot aggregation** (no HTTP server; useful for cron jobs):

```bash
uv run python scripts/run_aggregator.py
# or
uv run -m ai_news_aggregater.main
```

**Alternate entrypoint** (dependency-injection / `AggregationService` in the repo root):

```bash
uv run python main.py
```

### Tests

```bash
uv run pytest
```

### Docker (app + database)

```bash
docker compose up --build
```

The app service expects `DATABASE_URL` pointing at the `db` service (see `docker-compose.yml`).

## Configuration

| Variable | Purpose | Default / notes |
|----------|---------|-----------------|
| `DATABASE_URL` | PostgreSQL connection string | Required in production |
| `OPENAI_API_KEY` | LLM access | Required for analysis |
| `OPENAI_BASE_URL` | Optional API base URL | For OpenAI-compatible proxies |
| `CONTENT_ANALYZER_MODEL` | Model id | Falls back to `gpt-4o-mini` in code if unset |
| `CUSTOM_FETCH_HOUR` | Scheduler / logging: preferred hour (0–23) | `8` |
| `SCHEDULER_ENABLED` | Enable scheduler when using `start_scheduler()` | `true` |
| `SCHEDULER_TIMEZONE` | Timezone name | `UTC` |
| `FETCHER_TIMEOUT`, `FETCHER_MAX_RETRIES`, `FETCHER_RETRY_DELAY` | HTTP / fetch behavior | See `ai_news_aggregater/config/settings.py` |
| `SMTP_SERVER`, `SMTP_PORT`, `SMTP_USERNAME`, `SMTP_PASSWORD`, `SMTP_USE_TLS` | Outbound email | Gmail-friendly defaults for server/port |
| `SENDGRID_API_KEY`, `SENDGRID_FROM_EMAIL` | Optional SendGrid | Optional extras |
| `WEBSHARE_USERNAME`, `WEBSHARE_PASSWORD` | YouTube transcript proxy | Optional |
| `ENVIRONMENT`, `DEBUG`, `LOG_LEVEL` | Runtime / logging | `development`, `false`, `INFO` |
| `API_KEY` | Protects POST/PATCH on `/api/v1/sources*`, `/api/v1/jobs/*` | Empty = no auth (dev only) |
| `API_HOST`, `PORT` / `API_PORT` | Uvicorn bind | `0.0.0.0`, `8000` |
| `SYNC_DEFAULT_SOURCES_ON_STARTUP` | Upsert default feeds/channels on API boot | `false` |
| `AGGREGATION_LOOKBACK_HOURS` | RSS/YouTube lookback window | `24` |
| `AGGREGATION_RSS_PER_FEED_LIMIT` | Max RSS entries per URL | `20` |

Active feed URLs and channel IDs are stored in **`ingestion_sources`** (Postgres). Bundled defaults exist only in `ai_news_aggregater/data/default_sources.py` for the **sync** endpoint / startup flag.

## HTTP API

| Method | Path | Auth |
|--------|------|------|
| GET | `/health` | — (shallow probe) |
| GET | `/api/v1/health` | — |
| GET | `/api/v1/sources` | — |
| POST | `/api/v1/sources` | `X-API-Key` if `API_KEY` set |
| PATCH | `/api/v1/sources/{id}` | `X-API-Key` if set |
| POST | `/api/v1/sources/sync-defaults` | `X-API-Key` if set |
| POST | `/api/v1/jobs/aggregate` | `X-API-Key` if set |
| GET | `/api/v1/news` | — |

OpenAPI UI: `http://localhost:8000/docs`

## Scheduling

- **FastAPI (default):** `AsyncIOScheduler` runs with the app when `SCHEDULER_ENABLED=true`, calling the same pipeline as the CLI once per day at `CUSTOM_FETCH_HOUR` in `SCHEDULER_TIMEZONE` (`ai_news_aggregater/api/main.py`).
- **External cron:** set `SCHEDULER_ENABLED=false` and hit `POST /api/v1/jobs/aggregate` or run `uv run -m ai_news_aggregater.main`.
- **Blocking worker:** `from ai_news_aggregater.scheduler.tasks import start_scheduler` then `start_scheduler()`.

`render.yaml` deploys a **web** service (Uvicorn on `$PORT`).

## Project layout

| Path | Role |
|------|------|
| `ai_news_aggregater/api/main.py` | FastAPI app, lifespan, scheduler |
| `ai_news_aggregater/api/routes.py` | HTTP routes |
| `ai_news_aggregater/core/pipeline.py` | `aggregate_and_email()` |
| `ai_news_aggregater/data/default_sources.py` | Default rows for sync only |
| `ai_news_aggregater/models/source.py` | `IngestionSource` model |
| `ai_news_aggregater/services/ingestion_source_service.py` | CRUD + `sync_defaults()` |
| `ai_news_aggregater/main.py` | CLI entry (pipeline) |
| `main.py` | Alternate DI orchestration |
| `scripts/run_aggregator.py` | One-shot CLI |
| `scripts/migrate_db.py` | `create_tables()` |
| `scripts/run_migrations.py` | Alembic |

Further detail: `ARCHITECTURE.md`, `DEVELOPMENT.md`, `QUICK_REFERENCE.md`.

## Deployment

- Set secrets via environment variables (never commit `.env`). Use **`API_KEY`**, **`OPENAI_API_KEY`**, and **`DATABASE_URL`** in production.
- Use a managed PostgreSQL instance and point `DATABASE_URL` at it.
- Build: `docker build -t ai-news-aggregater .`
- Run: `docker run -p 8000:8000 --env-file .env ai-news-aggregater`
- On first deploy, call **`POST /api/v1/sources/sync-defaults`** or enable **`SYNC_DEFAULT_SOURCES_ON_STARTUP=true`** so `ingestion_sources` is populated before aggregation runs.

## License

MIT
