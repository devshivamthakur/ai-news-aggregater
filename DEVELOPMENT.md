"""Development and contribution guidelines."""

# Development Guide

## Setting Up Development Environment

### Prerequisites

- Python 3.14+
- PostgreSQL 12+
- Virtual environment (venv/virtualenv)

### Installation

```bash
# Clone repository
git clone <repo-url>
cd ai-news-aggregater

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -e ".[dev]"

# Setup environment variables
cp .env.example .env
# Edit .env with your configuration
```

### Database Setup

```bash
# Create database
createdb ai_news

# Run migrations
alembic upgrade head
```

## Project Architecture Quick Reference

### Layers

```
Request/Scheduler
    ↓
    ├─→ Services (BusinessLogic)
    │   ├─→ Repositories (DataAccess)
    │   │   └─→ Database
    │   ├─→ Fetchers (Integration)
    │   ├─→ Email (Integration)
    │   └─→ Validators (Utils)
```

### Key Directories

| Directory | Purpose | Examples |
|-----------|---------|----------|
| `config/` | Configuration | Settings, environment |
| `models/` | SQLAlchemy ORM | News, User tables |
| `storage/` | Data access | Repositories, DB connection |
| `services/` | Business logic | NewsService, UserService |
| `fetchers/` | Content sources | WebScraper, RSSFeedScraper |
| `email/` | Communication | EmailSender, templates |
| `utils/` | Helpers | Validators, errors, container |
| `logging/` | Logging | Logger configuration |

## Development Workflow

### Creating a New Feature

1. **Plan the feature**
   - Identify affected layers
   - Design database schema if needed
   - Plan API/interfaces

2. **Create database model** (if needed)
   ```python
   # ai_news_aggregater/models/your_model.py
   from ai_news_aggregater.models.Base import Base
   
   class YourModel(Base):
       __tablename__ = "your_table"
       # Define columns
   ```

3. **Create migration**
   ```bash
   alembic revision --autogenerate -m "Add your_table"
   ```

4. **Create repository** (if data access needed)
   ```python
   # ai_news_aggregater/storage/repository.py
   class YourRepository(BaseRepository):
       def __init__(self, db: Session):
           from ai_news_aggregater.models import YourModel
           super().__init__(db, YourModel)
   ```

5. **Create service** (business logic)
   ```python
   # ai_news_aggregater/services/your_service.py
   class YourService:
       def __init__(self, db: Session):
           self.repo = YourRepository(db)
       
       def your_business_logic(self):
           pass
   ```

6. **Create tests**
   ```python
   # tests/test_your_feature.py
   def test_your_feature(test_db):
       service = YourService(test_db)
       # Test implementation
   ```

7. **Update container** (if service)
   ```python
   # ai_news_aggregater/utils/container.py
   # Add to ServiceContainer._register_services()
   self.register_factory('your_service', lambda: YourService(db))
   ```

8. **Write documentation**
   - Update ARCHITECTURE.md if adding new patterns
   - Add docstrings to all public methods
   - Create example usage

### Code Style

Follow PEP 8:

```bash
# Format code
black ai_news_aggregater/ main.py

# Check style
flake8 ai_news_aggregater/ main.py

# Type checking
mypy ai_news_aggregater/
```

### Testing

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_suite.py::TestNewsService

# With coverage
pytest --cov=ai_news_aggregater

# Verbose output
pytest -v
```

## Adding a New News Source

### Step 1: Create Fetcher Class

```python
# ai_news_aggregater/fetchers/your_fetcher.py
from ai_news_aggregater.fetchers.base import BaseFetcher
from datetime import datetime

class YourFetcher(BaseFetcher):
    def __init__(self, timeout: int = 15, max_retries: int = 3):
        super().__init__(timeout, max_retries)
        # Initialize source-specific settings
    
    def fetch(self):
        """Fetch articles from your source."""
        articles = []
        
        try:
            # Your fetching logic here
            items = self._fetch_items()
            
            for item in items:
                if self.validate_data(item):
                    articles.append({
                        'url': item['url'],
                        'title': item['title'],
                        'content': self.sanitize_text(item['content']),
                        'summary': item['summary'],
                        'category': item['category'],
                        'published_at': self.ensure_published_date(item['date']),
                        'source': 'Your Source Name',
                        'news_type': NewsType.ARTICLE
                    })
            
            self.log_fetch_summary(len(articles), duration=0)
            return articles
            
        except Exception as e:
            logger.error(f"Error fetching from YourSource: {e}")
            return []
    
    def validate_data(self, item):
        """Validate item structure."""
        required = ['url', 'title', 'content']
        return all(key in item and item[key] for key in required)
    
    def _fetch_items(self):
        """Your actual fetch implementation."""
        pass
```

### Step 2: Register Fetcher

```python
# ai_news_aggregater/utils/container.py
def _register_fetchers(self, settings):
    from ai_news_aggregater.fetchers.your_fetcher import YourFetcher
    
    self.register_factory(
        'your_fetcher',
        lambda: YourFetcher(settings.fetcher.timeout, settings.fetcher.max_retries)
    )
```

### Step 3: Integrate with Aggregator

```python
# main.py
sources = [
    # ... existing sources
    ('your_fetcher', YourFetcher(), 'Your Source'),
]
```

## Database Migrations

### Create a Migration

```bash
# Auto-detect changes
alembic revision --autogenerate -m "Describe changes"

# Create empty migration
alembic revision -m "Describe changes"
```

### Migration Template

```python
# alembic/versions/001_add_column.py
from alembic import op
import sqlalchemy as sa

def upgrade():
    op.add_column('news', sa.Column('new_column', sa.String()))

def downgrade():
    op.drop_column('news', 'new_column')
```

### Apply Migrations

```bash
# Run pending migrations
alembic upgrade head

# Revert last migration
alembic downgrade -1

# View migration history
alembic history
```

## Common Tasks

### Add a New Service

```python
# 1. Create service class
class MyService:
    def __init__(self, db: Session):
        self.repo = MyRepository(db)
    
    def my_method(self):
        pass

# 2. Register in container
# container.py: self.register_factory('my_service', lambda: MyService(db))

# 3. Use in code
service = get_service('my_service')
```

### Add Email Template

```html
<!-- ai_news_aggregater/email/templates/my_template.html -->
<!DOCTYPE html>
<html>
<head>
    <title>{{ subject }}</title>
</head>
<body>
    <h1>Hello {{ user_name }}</h1>
    {% for article in articles %}
        <article>
            <h2>{{ article.title }}</h2>
            <p>{{ article.summary }}</p>
        </article>
    {% endfor %}
</body>
</html>
```

Then use:

```python
template_html = email_sender.render_template('my_template.html', **context)
```

### Add Configuration Option

```python
# ai_news_aggregater/config/settings.py
class MyConfig(BaseModel):
    my_setting: str = os.getenv("MY_SETTING", "default")

class Settings(BaseModel):
    my_config: MyConfig = MyConfig()
```

Environment variable:
```bash
MY_SETTING=value
```

## Debugging

### Enable Debug Logging

```bash
export LOG_LEVEL=DEBUG
python main.py
```

### Debug Database Queries

```python
from sqlalchemy import event
from sqlalchemy.engine import Engine

@event.listens_for(Engine, "before_cursor_execute")
def receive_before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    print(f"SQL: {statement}")
    print(f"PARAMS: {parameters}")
```

### Profiling Code

```python
from ai_news_aggregater.utils.errors import measure_execution_time

@measure_execution_time
def my_function():
    pass
```

## Performance Optimization

### Database Indexing

```python
# In model definition
from sqlalchemy import Index

class News(Base):
    __tablename__ = "news"
    
    url = Column(String, unique=True, nullable=False, index=True)
    category = Column(String, index=True)
    fetch_hour = Column(Integer, index=True)
    
    __table_args__ = (
        Index('idx_category_fetch_hour', 'category', 'fetch_hour'),
    )
```

### Connection Pooling

```python
# Already optimized in db.py
engine = create_engine(
    settings.database_url,
    pool_size=10,           # Connection pool size
    max_overflow=20,        # Extra connections when pool full
    pool_timeout=30,        # Wait timeout in seconds
    pool_recycle=1800       # Recycle connections every 30min
)
```

### Query Optimization

```python
# Use eager loading to avoid N+1 queries
from sqlalchemy.orm import joinedload

users = db.query(User).options(joinedload(User.articles)).all()
```

## Production Deployment

### Environment Variables

See `.env.example` for all required variables.

### Docker

```dockerfile
# Dockerfile is pre-configured
docker build -t ai-news-aggregater .
docker-compose up
```

### Monitoring

- Enable logging to file
- Set up log rotation
- Monitor database connections
- Track error rates

### Backup Strategy

```bash
# Backup PostgreSQL database
pg_dump ai_news > backup.sql

# Restore from backup
psql ai_news < backup.sql
```

## Contributing

1. Create a feature branch: `git checkout -b feature/your-feature`
2. Write tests for your code
3. Ensure all tests pass: `pytest`
4. Format code: `black ai_news_aggregater/`
5. Create pull request with description

## Useful Commands

```bash
# Run application
python main.py

# Run tests
pytest -v

# Check code style
black --check ai_news_aggregater/

# Format code
black ai_news_aggregater/

# Type checking
mypy ai_news_aggregater/

# Database shell
psql ai_news

# View logs
tail -f /var/log/aggregator.log
```

## Troubleshooting

### Database Connection Issues

```bash
# Check PostgreSQL is running
psql postgres -U postgres -c "SELECT version();"

# Check environment variables
echo $DATABASE_URL
```

### Import Errors

```bash
# Verify package installation
pip show ai-news-aggregater

# Reinstall in development mode
pip install -e .
```

### Migration Issues

```bash
# Check current migration status
alembic current

# View all migrations
alembic history

# Reset to clean state (development only!)
alembic downgrade base
```
