"""Guide for migrating from old to new architecture patterns."""

# Migration Guide: From Function-Based to Class-Based Architecture

## Overview

This guide helps you update your code to use the new optimized, scalable architecture.

## 1. Database Access Migration

### Before: Function-Based CRUD

```python
from ai_news_aggregater.storage.crud import create_news, get_news_by_category

# Create news
db = get_db()
news = create_news(
    db=db,
    title="Article",
    content="Content...",
    summary="Summary",
    category="AI",
    source="Blog",
    url="https://example.com",
    published_at=datetime.utcnow(),
    news_type=NewsType.ARTICLE,
    fetch_hour=8
)

# Get news
articles = get_news_by_category(db, "AI")
```

### After: Repository Pattern

```python
from ai_news_aggregater.storage.repository import NewsRepository
from ai_news_aggregater.storage.db import SessionLocal

# Create repository
db = SessionLocal()
news_repo = NewsRepository(db)

# Create news with automatic duplicate detection
news, is_new = news_repo.get_or_create(
    url="https://example.com",  # Checked for duplicates
    title="Article",
    content="Content...",
    summary="Summary",
    category="AI",
    source="Blog",
    published_at=datetime.utcnow(),
    news_type=NewsType.ARTICLE,
    fetch_hour=8
)

if is_new:
    print("Created new article")
else:
    print("Article already exists")

# Get news
articles = news_repo.get_by_category("AI")
```

**Benefits:**
- Automatic duplicate prevention
- Type safety with class methods
- Better error handling
- Cleaner API

---

## 2. Business Logic Migration

### Before: Direct CRUD Usage

```python
from ai_news_aggregater.storage.crud import create_news, create_user
from ai_news_aggregater.storage.db import get_db

db = get_db()

# Create user
user = create_user(db, "John", "john@example.com", ["AI", "ML"])

# Create article
article = create_news(
    db, "Title", "Content", "Summary", "AI", "Blog",
    "https://example.com", datetime.utcnow()
)
```

### After: Service Layer

```python
from ai_news_aggregater.services.news_service import NewsService, UserService
from ai_news_aggregater.storage.db import SessionLocal

db = SessionLocal()

# Use services with business logic
user_service = UserService(db)
news_service = NewsService(db)

# Register user with validation
user, is_new = user_service.register_user(
    email="john@example.com",
    name="John",
    interests=["AI", "ML"]
)

# Add article with business rules
article, is_new = news_service.add_article(
    url="https://example.com",
    title="Title",
    content="Content",
    summary="Summary",
    category="AI",
    source="Blog",
    published_at=datetime.utcnow()
)
```

**Benefits:**
- Input validation
- Business logic centralized
- Consistent error handling
- Easier to test

---

## 3. Data Fetching Migration

### Before: Direct Processing

```python
from ai_news_aggregater.fetchers.web_fetcher import fetch_web_content
from ai_news_aggregater.storage.crud import create_news

db = get_db()

# Fetch content
content = fetch_web_content("https://example.com")

# Store manually
if content:
    news = create_news(
        db,
        title=content.title,
        content=content.content,
        # ... other fields
    )
```

### After: Service Orchestration

```python
from ai_news_aggregater.fetchers.web_fetcher import WebScraper
from ai_news_aggregater.services.news_service import AggregationService

db = SessionLocal()
aggregation = AggregationService(db)

# Fetch articles
fetcher = WebScraper()
articles = fetcher.fetch()

# Process with orchestration service
stats = aggregation.process_fetched_articles(articles, "Web Source")

# Automatic duplicate handling, logging, statistics
print(f"Created: {stats['created']}, Skipped: {stats['skipped']}")
```

**Benefits:**
- Automatic duplicate detection
- Standardized error handling
- Built-in statistics
- Easier to chain operations

---

## 4. Configuration Migration

### Before: Direct Access

```python
from ai_news_aggregater.config.settings import settings

db_url = settings.database_url
smtp_port = settings.smtp_port
fetch_hour = settings.custom_fetch_hour
```

### After: Organized Structure

```python
from ai_news_aggregater.config.settings import settings

# Access organized configs
db_url = settings.database.url
smtp_port = settings.smtp.port
fetch_hour = settings.scheduler.fetch_hour

# Backward compatible (still works)
db_url = settings.database_url
fetch_hour = settings.custom_fetch_hour
```

**Benefits:**
- Better organization
- Type hints for IDE support
- Easier to discover settings
- Backward compatible

---

## 5. Error Handling Migration

### Before: Manual Try-Catch

```python
try:
    articles = fetcher.fetch()
except Exception as e:
    print(f"Error: {e}")
    articles = []
```

### After: Decorator-Based

```python
from ai_news_aggregater.utils.errors import (
    retry_on_failure,
    handle_errors,
    validate_args
)
from ai_news_aggregater.utils.validators import Validators

@retry_on_failure(max_retries=3, delay=2.0)
@validate_args(email=Validators.is_valid_email)
def process_user(email: str):
    # Automatically retries on failure
    # Validates email before execution
    pass
```

**Benefits:**
- Declarative error handling
- Automatic retries with backoff
- Input validation
- Consistent logging

---

## 6. Dependency Injection Migration

### Before: Direct Instantiation

```python
from ai_news_aggregater.storage.db import SessionLocal
from ai_news_aggregater.services.news_service import NewsService

db = SessionLocal()
service = NewsService(db)

# Later in code...
db2 = SessionLocal()  # Separate instance
service2 = NewsService(db2)
```

### After: Container

```python
from ai_news_aggregater.utils.container import setup_container, get_service

# Initialize once at startup
setup_container(db_session, settings)

# Get services anywhere
service = get_service('news_service')

# All use the same managed instances
```

**Benefits:**
- Single source of truth
- Cleaner code
- Easier testing
- Lifecycle management

---

## 7. Testing Migration

### Before: Minimal Testing

```python
def test_create_news():
    db = get_db()
    news = create_news(db, "Title", "Content", ...)
    assert news.title == "Title"
```

### After: Comprehensive Testing

```python
from tests.test_suite import test_db
from ai_news_aggregater.services.news_service import NewsService

def test_add_article_duplicate(test_db):
    service = NewsService(test_db)
    
    # First create
    article1, is_new1 = service.add_article(
        url="https://example.com",
        title="Title",
        # ... other fields
    )
    assert is_new1 == True
    
    # Second with same URL
    article2, is_new2 = service.add_article(
        url="https://example.com",
        title="Different Title",
        # ... other fields
    )
    assert is_new2 == False
    assert article1.id == article2.id
```

**Benefits:**
- Better test fixtures
- Automatic duplicate testing
- More realistic scenarios

---

## Migration Checklist

- [ ] Replace `create_news` calls with `NewsService.add_article()`
- [ ] Replace `create_user` calls with `UserService.register_user()`
- [ ] Update database access to use repositories
- [ ] Migrate error handling to decorators
- [ ] Update fetcher instantiation to use service container
- [ ] Update configuration access to organized structure
- [ ] Add input validation using validators
- [ ] Update tests to use new service layer
- [ ] Update main.py to use new architecture
- [ ] Test duplicate detection scenarios

---

## Common Patterns

### Adding a New Fetcher

```python
from ai_news_aggregater.fetchers.base import BaseFetcher

class MyFetcher(BaseFetcher):
    def fetch(self):
        # Implement fetch logic
        pass
    
    def validate_data(self, item):
        # Implement validation
        pass

# Register if using container
from ai_news_aggregater.utils.container import get_container
fetcher = MyFetcher()
get_container().register_singleton('my_fetcher', fetcher)
```

### Processing Articles

```python
from ai_news_aggregater.services.news_service import AggregationService

service = AggregationService(db)

# Process batch
stats = service.process_fetched_articles(articles, "Source Name")

# Check results
print(f"Success: {stats['created'] + stats['skipped']} processed, "
      f"{stats['errors']} errors")
```

### Querying with Filters

```python
from ai_news_aggregater.storage.repository import NewsRepository

repo = NewsRepository(db)

# Simple filters
ai_articles = repo.get_by_category("AI")
web_articles = repo.get_by_source("Web")

# Advanced: use filter method
articles = repo.filter(
    category="AI",
    source="Blog"
)

# Pagination
page1, total = repo.paginate(page=1, page_size=10)
```

---

## FAQ

**Q: Should I keep the old CRUD functions?**
A: No, migrate completely. The services provide better abstractions.

**Q: Can I mix old and new code?**
A: Not recommended. Migrate entire features at once.

**Q: How do I handle transactions?**
A: Repositories and services handle transactions internally. For complex flows, manage sessions explicitly.

**Q: What about async code?**
A: Current implementation is synchronous. For async, use SQLAlchemy async drivers with adapters.

**Q: Is there a performance impact?**
A: No, often better due to connection pooling and smarter queries.
