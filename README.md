# AI News Aggregator

An AI-powered news aggregator that fetches news from various sources (videos, blogs like OpenAI/Anthropic, websites, Medium), categorizes them, stores in PostgreSQL, and emails personalized summaries based on user interests. Features custom hourly scheduling in 24-hour format.

## Features

- Fetches news from multiple sources
- AI-driven categorization and summarization
- PostgreSQL storage with fetch tracking
- Personalized email notifications
- **Custom hourly scheduling (0-23 24-hour format)**
- Retry logic with exponential backoff
- Comprehensive logging

## Setup

1. Clone the repository
2. Install dependencies: `pip install -e .`
3. Copy `.env.example` to `.env` and configure:
   - PostgreSQL connection string
   - OpenAI API key
   - Email settings (SMTP or SendGrid)
   - **Custom fetch hour (0-23)**
4. Run migrations: `python scripts/migrate_db.py`
5. Seed initial users: `python scripts/seed_data.py`

## Configuration

Set your custom fetch hour in `.env`:
```
CUSTOM_FETCH_HOUR=8    # 24-hour format (0-23)
```

For detailed configuration options, see [docs/hourly_configuration.md](docs/hourly_configuration.md).

## Usage

### Manual Run
```bash
make run
```

### Tests
```bash
make test
```

### Database Operations
```bash
make migrate    # Run migrations
make seed       # Seed initial data
```

### Docker
```bash
docker-compose up
```

### Scheduler (Continuous)
The scheduler starts daily at your configured hour:
```python
from ai_news_aggregater.scheduler.tasks import start_scheduler
start_scheduler()  # Runs indefinitely until stopped
```

## Database Schema

### News Table
- `id`: Primary key
- `title`, `content`, `summary`: Article content
- `category`: AI-categorized topic
- `source`: Source website/blog
- `url`: Article URL
- `news_type`: ARTICLE, VIDEO, or BLOG_POST
- `fetch_hour`: Hour (0-23) when fetched
- `fetch_date`: Timestamp of fetch
- `created_at`: Record creation time

### Users Table
- `id`: Primary key
- `email`: User email
- `interests`: JSON array of preferred categories
- `created_at`, `updated_at`: Timestamps

## Deployment

### Docker
Build and run:
```bash
docker build -t ai-news-aggregater .
docker run -e DATABASE_URL=... -e OPENAI_API_KEY=... ai-news-aggregater
```

### Production
- Use PostgreSQL service (RDS, Cloud SQL, etc.)
- Set environment variables for secrets
- Deploy as containerized service
- Use `start_scheduler()` for continuous operation

## Monitoring

Logs include:
- Fetch timestamps and hour
- Processing status
- Storage confirmations
- Email delivery status
- Error details with retry attempts

## Contributing

Contributions welcome! Please:
1. Add tests for new features
2. Update documentation
3. Follow existing code style

## License

MIT