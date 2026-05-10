"""Architecture and usage documentation for the AI News Aggregator."""

# AI News Aggregator - Architecture Guide

## Project Structure

```
ai-news-aggregater/
├── ai_news_aggregater/
│   ├── config/              # Configuration management
│   │   └── settings.py      # Modular settings with validation
│   ├── models/              # SQLAlchemy database models
│   │   ├── base.py
│   │   ├── news.py
│   │   └── user.py
│   ├── storage/             # Data access layer
│   │   ├── db.py            # Database connection
│   │   ├── crud.py          # Legacy function-based operations
│   │   └── repository.py    # New class-based repository pattern
│   ├── services/            # Business logic layer
│   │   └── news_service.py  # Service classes for domain logic
│   ├── fetchers/            # News fetching implementations
│   │   ├── base.py          # Abstract BaseFetcher class
│   │   ├── web_fetcher.py   # WebScraper for websites
│   │   ├── blog_fetcher.py  # RSSFeedScraper for blogs
│   │   ├── video_fetcher.py # YouTubeScraper for videos
│   │   └── models.py        # Pydantic models for fetched data
│   ├── email/               # Email sending system
│   │   ├── sender.py        # EmailSender class
│   │   └── templates/       # Jinja2 HTML templates
│   ├── scheduler/           # APScheduler integration
│   │   └── tasks.py         # Scheduled job definitions
│   ├── logging/             # Logging configuration
│   │   └── logger.py        # Logger setup
│   └── utils/               # Utility modules
│       ├── errors.py        # Custom exceptions and decorators
│       ├── validators.py    # Validation functions
│       └── container.py     # Dependency injection
├── alembic/                 # Database migrations
├── main.py                  # Application entry point
├── pyproject.toml           # Project dependencies
└── README.md
```

## Architecture Patterns

### 1. Repository Pattern

Provides a clean abstraction over database access with automatic duplicate detection:

```python
from ai_news_aggregater.storage.repository import NewsRepository, UserRepository
from ai_news_aggregater.storage.db import SessionLocal

db = SessionLocal()

# Create repositories
news_repo = NewsRepository(db)
user_repo = UserRepository(db)

# Get or create with duplicate checking
news, is_new = news_repo.get_or_create(
    url="https://example.com/article",
    title="Article Title",
    content="Article content...",
    # ... other fields
)

# Query
articles = news_repo.get_by_category("AI")
```

### 2. Service Layer

Encapsulates business logic and orchestration:

```python
from ai_news_aggregater.services.news_service import (
    NewsService, UserService, AggregationService
)

db = SessionLocal()

# Services handle validation and business rules
news_service = NewsService(db)
user_service = UserService(db)
aggregation = AggregationService(db)

# Add article with automatic duplicate prevention
article, is_new = news_service.add_article(
    url="https://example.com",
    title="Title",
    content="Content",
    summary="Summary",
    category="AI",
    source="Blog",
    published_at=datetime.utcnow()
)

# Get personalized digest
digest = aggregation.get_personalized_digest("user@example.com")
```

### 3. Fetcher Pattern (Strategy Pattern)

Unified interface for all content sources:

```python
from ai_news_aggregater.fetchers.base import BaseFetcher
from ai_news_aggregater.fetchers.web_fetcher import WebScraper
from ai_news_aggregater.fetchers.blog_fetcher import RSSFeedScraper

# All fetchers implement the same interface
web_scraper = WebScraper(timeout=15, max_retries=3)
rss_scraper = RSSFeedScraper(timeout=15, max_retries=3)

# Consistent API across sources
articles_web = web_scraper.fetch()
articles_rss = rss_scraper.fetch()
```

### 4. Dependency Injection Container

Centralized service management:

```python
from ai_news_aggregater.utils.container import setup_container, get_service

# Initialize on startup
setup_container(db_session, settings)

# Get services anywhere
news_service = get_service('news_service')
email_sender = get_service('email_sender')
```

### 5. Configuration Management

Modular, validated configuration with backward compatibility:

```python
from ai_news_aggregater.config.settings import settings

# Access organized configs
database_url = settings.database.url
smtp_timeout = settings.smtp.port
fetch_hour = settings.scheduler.fetch_hour

# Backward compatible properties
db_url = settings.database_url
hour = settings.custom_fetch_hour
```

## Key Features

### Automatic Duplicate Detection

All data operations check for existing records before insertion:

- **News**: Checks by URL before creating article
- **Users**: Checks by email before creating user
- Returns tuple `(record, is_new)` indicating if newly created

### Error Handling

Comprehensive exception hierarchy with custom decorators:

```python
from ai_news_aggregater.utils.errors import (
    retry_on_failure,
    handle_errors,
    validate_args,
)

@retry_on_failure(max_retries=3, delay=2.0, backoff=1.0)
@validate_args(email=Validators.is_valid_email)
def process_user(email: str):
    pass
```

### Logging

Structured logging throughout the application:

```python
from ai_news_aggregater.logging.logger import logger

logger.info("Processing started")
logger.warning("Duplicate found, skipping")
logger.error("Failed to fetch: {error}")
```

## Usage Examples

### Initialize and Run Full Cycle

```python
from main import initialize_database, fetch_and_store_articles, send_digests

# Setup
initialize_database()

# Fetch articles
fetch_and_store_articles()

# Send to users
send_digests()
```

### Add a New User

```python
from ai_news_aggregater.services.news_service import UserService
from ai_news_aggregater.storage.db import SessionLocal

db = SessionLocal()
user_service = UserService(db)

# Register user (automatic duplicate prevention)
user, is_new = user_service.register_user(
    email="user@example.com",
    name="John Doe",
    interests=["AI", "Machine Learning"]
)

if is_new:
    print(f"New user registered: {user.name}")
else:
    print(f"User already exists: {user.name}")
```

### Fetch and Store Articles

```python
from ai_news_aggregater.services.news_service import AggregationService
from ai_news_aggregater.fetchers.web_fetcher import WebScraper

db = SessionLocal()
aggregation = AggregationService(db)

# Fetch from source
fetcher = WebScraper()
articles = fetcher.fetch()

# Process with automatic duplicate handling
stats = aggregation.process_fetched_articles(articles, "My Blog")
print(f"Created: {stats['created']}, Skipped: {stats['skipped']}")
```

### Send Personalized Digest

```python
from ai_news_aggregater.services.news_service import AggregationService
from ai_news_aggregater.email.sender import EmailSender

db = SessionLocal()
aggregation = AggregationService(db)
email_sender = EmailSender()

# Get digest for user
digest = aggregation.get_personalized_digest("user@example.com", limit=5)

if digest:
    # Send email
    email_sender.send_news_digest(
        user_email=digest['user']['email'],
        user_name=digest['user']['name'],
        articles=[...],
        user_interests=digest['user']['interests']
    )
```

## Configuration

Environment variables for customization:

```bash
# Database
DATABASE_URL=postgresql://user:pass@localhost/ai_news
DB_POOL_SIZE=10
DB_POOL_TIMEOUT=30

# Email - SMTP
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your@email.com
SMTP_PASSWORD=your_password

# Email - SendGrid (alternative)
SENDGRID_API_KEY=your_key
SENDGRID_FROM_EMAIL=from@example.com

# Fetchers
FETCHER_TIMEOUT=15
FETCHER_MAX_RETRIES=3
FETCHER_RETRY_DELAY=2.0
FETCHER_CONTENT_MAX_LENGTH=5000

# Scheduler
CUSTOM_FETCH_HOUR=8  # 0-23
SCHEDULER_ENABLED=true
SCHEDULER_TIMEZONE=UTC

# Logging
LOG_LEVEL=INFO
LOG_FILE=/var/log/aggregator.log

# Application
ENVIRONMENT=production
DEBUG=false

# API Keys
OPENAI_API_KEY=your_key
ANTHROPIC_API_KEY=your_key
```

## Testing Strategies

### Unit Testing Repositories

```python
from sqlalchemy.orm import Session
from ai_news_aggregater.storage.repository import NewsRepository
from ai_news_aggregater.models import News

def test_news_duplicate_detection(db: Session):
    repo = NewsRepository(db)
    
    # First create should succeed
    article1, is_new = repo.get_or_create(
        url="https://example.com",
        title="Article"
    )
    assert is_new == True
    
    # Second with same URL should return existing
    article2, is_new = repo.get_or_create(
        url="https://example.com",
        title="Different Title"
    )
    assert is_new == False
    assert article1.id == article2.id
```

### Unit Testing Services

```python
from ai_news_aggregater.services.news_service import NewsService

def test_category_filtering(db: Session):
    service = NewsService(db)
    
    articles = service.get_news_by_category("AI")
    assert all(a.category == "AI" for a in articles)
```

## Best Practices

1. **Always use Services for business logic** - Never query repositories directly in application code
2. **Let repositories handle duplicates** - Use `get_or_create` methods
3. **Validate inputs** - Use validators in utils/validators.py
4. **Log important operations** - Use the logger throughout
5. **Handle exceptions explicitly** - Use custom exceptions and decorators
6. **Keep transactions small** - Close sessions promptly
7. **Use dependency injection** - Get services from container

## Migration

### From old function-based CRUD to new repository pattern

**Old:**
```python
from ai_news_aggregater.storage.crud import create_news, get_news_by_category

news = create_news(db, title=..., content=..., ...)
articles = get_news_by_category(db, "AI")
```

**New:**
```python
from ai_news_aggregater.services.news_service import NewsService

service = NewsService(db)
news, is_new = service.add_article(title=..., content=..., ...)
articles = service.get_news_by_category("AI")
```

## Performance Considerations

- **Database pooling**: Configured via settings with pool_size and max_overflow
- **Connection recycling**: pool_recycle set to 1800s (30 min) to handle stale connections
- **Lazy loading**: SQLAlchemy relationships use lazy loading by default
- **Batch operations**: Use `batch_list` helper for processing large datasets
- **Caching**: Settings use @lru_cache for singleton pattern

## Scalability

The architecture supports:

- **Multi-source fetching**: Add new fetchers by extending BaseFetcher
- **Horizontal scaling**: Services are stateless, can run in multiple processes
- **Queue processing**: Repository pattern supports async queue workers
- **Database optimization**: Use Alembic migrations to add indexes and partitioning
- **Service separation**: Services layer can be extracted to microservices
