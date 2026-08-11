"""Quick reference for common operations."""

# Quick Reference Card

## Common Operations

### Add News Article

```python
from ai_news_aggregater.services.news_service import NewsService
from ai_news_aggregater.storage.db import SessionLocal

db = SessionLocal()
service = NewsService(db)

article, is_new = service.add_article(
    url="https://example.com/article",
    title="Article Title",
    content="Full content...",
    summary="Brief summary",
    category="AI",
    source="Blog Name",
    published_at=datetime.utcnow()
)

# Returns (article_record, True/False)
# False means duplicate was found
```

### Register User

```python
from ai_news_aggregater.services.news_service import UserService

user_service = UserService(db)

user, is_new = user_service.register_user(
    email="user@example.com",
    name="John Doe",
    interests=["AI", "Machine Learning"]
)
```

### Get Personalized Digest

```python
from ai_news_aggregater.services.news_service import AggregationService

agg_service = AggregationService(db)

digest = agg_service.get_personalized_digest(
    email="user@example.com",
    limit=10  # Max articles
)

if digest:
    print(f"Found {len(digest['articles'])} articles")
    for article in digest['articles']:
        print(f"  - {article.title}")
```

### Send Email

```python
from ai_news_aggregater.email.sender import EmailSender

email_sender = EmailSender()

success = email_sender.send_news_digest(
    user_email="user@example.com",
    user_name="John",
    articles=[...],
    user_interests=["AI"]
)
```

### Query Articles

```python
from ai_news_aggregater.storage.repository import NewsRepository

repo = NewsRepository(db)

# Get by category
ai_articles = repo.get_by_category("AI")

# Get by source
blog_articles = repo.get_by_source("OpenAI Blog")

# Get recent
recent = repo.get_recent(limit=5)

# Get by hour
hour_8 = repo.get_by_hour(8)

# Advanced filtering
articles = repo.filter(category="AI", source="Blog")

# Pagination
page1, total = repo.paginate(page=1, page_size=10)
```

### Query Users

```python
from ai_news_aggregater.storage.repository import UserRepository

user_repo = UserRepository(db)

# Get active users
active = user_repo.get_active_users()

# Get by interest
interested = user_repo.get_by_interests(["AI", "ML"])

# Get by email
user = user_repo.get_by_email("user@example.com")
```

## Configuration Quick Reference

```python
from ai_news_aggregater.config.settings import settings

# Database
settings.database.url
settings.database.pool_size

# Email
settings.smtp.server
settings.smtp.port
settings.smtp.username

# Scheduler
settings.scheduler.fetch_hour
settings.scheduler.enabled

# Logging
settings.logging.level
settings.logging.file

# Backward compatible
settings.database_url
settings.custom_fetch_hour
```

## Error Handling

```python
from ai_news_aggregater.utils.errors import (
    retry_on_failure,
    validate_args,
    FetchError
)
from ai_news_aggregater.utils.validators import Validators

# Automatic retries
@retry_on_failure(max_retries=3, delay=2.0)
def fetch_data():
    pass

# Validate arguments
@validate_args(email=Validators.is_valid_email)
def process_user(email: str):
    pass

# Custom exceptions
raise FetchError("Failed to fetch", source="OpenAI")
```

## Logging

```python
from ai_news_aggregater.logging.logger import logger

logger.info("Processing started")
logger.warning("Duplicate found")
logger.error("Failed to process")
logger.debug("Debug information")
```

## Testing

```python
from tests.test_suite import test_db
import pytest

@pytest.fixture
def db_session(test_db):
    return test_db

def test_something(db_session):
    from ai_news_aggregater.services.news_service import NewsService
    service = NewsService(db_session)
    # Test implementation
```

## Validators

```python
from ai_news_aggregater.utils.validators import (
    Validators, TextHelpers, CollectionHelpers
)

# Validate
Validators.is_valid_email("test@example.com")
Validators.is_valid_url("https://example.com")
Validators.is_valid_hour(8)

# Text operations
TextHelpers.truncate("Long text", max_length=20)
TextHelpers.estimate_reading_time(article_text)
TextHelpers.extract_domain("https://example.com/page")

# Collection operations
CollectionHelpers.remove_duplicates([1, 2, 2, 3])
CollectionHelpers.batch_list([1, 2, 3, 4], batch_size=2)
```

## Fetchers

```python
from ai_news_aggregater.fetchers.web_fetcher import WebScraper
from ai_news_aggregater.fetchers.blog_fetcher import RSSFeedScraper
from ai_news_aggregater.fetchers.video_fetcher import YouTubeScraper

# Create fetcher
web_scraper = WebScraper(timeout=15, max_retries=3)

# Fetch articles
articles = web_scraper.fetch()

# Process articles
for article in articles:
    print(article['title'])
    print(article['url'])
```

## Repository Operations

```python
from ai_news_aggregater.storage.repository import NewsRepository

repo = NewsRepository(db)

# Create with duplicate check
news, is_new = repo.get_or_create(
    url="https://example.com",
    title="Title",
    content="Content"
)

# Basic CRUD
repo.create(obj)
repo.get_by_id(1)
repo.update(1, {'title': 'New Title'})
repo.delete(1)

# Query
repo.get_all()
repo.filter(category="AI")
repo.filter_one(url="...")

# Pagination
records, total = repo.paginate(page=1, page_size=10)

# Count
count = repo.count()
```

## Services

```python
# Create services
news_service = NewsService(db)
user_service = UserService(db)
agg_service = AggregationService(db)

# News operations
news_service.add_article(...)
news_service.get_news_by_category(...)
news_service.get_news_by_hour(...)
news_service.get_recent_news(...)
news_service.search_news("query")

# User operations
user_service.register_user(...)
user_service.get_user(email)
user_service.get_active_users()
user_service.get_users_by_interests([...])
user_service.deactivate_user(email)

# Aggregation
digest = agg_service.get_personalized_digest(email)
stats = agg_service.process_fetched_articles(articles, source)
```

## Dependency Injection

```python
from ai_news_aggregater.utils.container import (
    setup_container,
    get_service
)

# Initialize at startup
setup_container(db_session, settings)

# Get services anywhere
news_service = get_service('news_service')
user_service = get_service('user_service')
email_sender = get_service('email_sender')
```

## Database

```python
from ai_news_aggregater.storage.db import (
    SessionLocal,
    create_tables,
    get_db
)

# Create session
db = SessionLocal()

# Create tables
create_tables()

# Context manager
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

## Quick Start

```python
from main import initialize_database, fetch_and_store_articles, send_digests

# Setup
initialize_database()

# Run aggregation
fetch_and_store_articles()

# Send emails
send_digests()
```

## Environment Setup

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate

# Install package
pip install -e .

# Setup database
createdb ai_news
alembic upgrade head

# Run application
python main.py
```

## Files to Know

| File | Purpose |
|------|---------|
| `main.py` | Application entry point |
| `config/settings.py` | Configuration |
| `models/` | Database models |
| `storage/repository.py` | Data access |
| `services/news_service.py` | Business logic |
| `fetchers/` | News sources |
| `email/sender.py` | Email sending |
| `utils/errors.py` | Error handling |
| `utils/validators.py` | Validation helpers |
| `utils/container.py` | Dependency injection |
| `ARCHITECTURE.md` | System design |
| `MIGRATION_GUIDE.md` | Updating code |
| `DEVELOPMENT.md` | Setup & development |

## Common Issues

**Import Error**
```bash
pip install -e .
```

**Database Connection**
```bash
export DATABASE_URL=postgresql://user:pass@localhost/ai_news
psql $DATABASE_URL -c "SELECT 1"
```

**Migration Issues**
```bash
alembic downgrade base  # Reset
alembic upgrade head    # Run all
```

**Email Not Sending**
```bash
# Check SMTP settings
echo $SMTP_SERVER
echo $SMTP_USERNAME
# Test with logger
export LOG_LEVEL=DEBUG
```
