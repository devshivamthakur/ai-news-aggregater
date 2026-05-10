"""Testing utilities and fixtures for the aggregator."""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime
from ai_news_aggregater.models import Base, News, User
from ai_news_aggregater.models.news import NewsType


@pytest.fixture
def test_db():
    """Create in-memory SQLite database for testing."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    yield db
    
    db.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def sample_news(test_db: Session) -> News:
    """Create a sample news article."""
    news = News(
        title="Test Article",
        content="Test content...",
        summary="Test summary",
        category="AI",
        source="Test Source",
        url="https://example.com/test",
        published_at=datetime.utcnow(),
        news_type=NewsType.ARTICLE,
        fetch_hour=8,
        fetch_date=datetime.utcnow()
    )
    test_db.add(news)
    test_db.commit()
    return news


@pytest.fixture
def sample_user(test_db: Session) -> User:
    """Create a sample user."""
    user = User(
        email="test@example.com",
        name="Test User",
        interests=["AI", "Technology"]
    )
    test_db.add(user)
    test_db.commit()
    return user


class TestRepository:
    """Test repository operations."""
    
    def test_get_or_create_new(self, test_db: Session):
        """Test creating new record."""
        from ai_news_aggregater.storage.repository import NewsRepository
        
        repo = NewsRepository(test_db)
        news, is_new = repo.get_or_create(
            url="https://example.com/new",
            title="New Article",
            content="Content",
            summary="Summary",
            category="AI",
            source="Test"
        )
        
        assert is_new == True
        assert news.url == "https://example.com/new"
    
    def test_get_or_create_existing(self, test_db: Session, sample_news: News):
        """Test getting existing record."""
        from ai_news_aggregater.storage.repository import NewsRepository
        
        repo = NewsRepository(test_db)
        news, is_new = repo.get_or_create(
            url=sample_news.url,
            title="Different Title",
            content="Different content"
        )
        
        assert is_new == False
        assert news.id == sample_news.id
        assert news.title == sample_news.title  # Original title preserved


class TestNewsService:
    """Test news service operations."""
    
    def test_add_article_new(self, test_db: Session):
        """Test adding new article."""
        from ai_news_aggregater.services.news_service import NewsService
        
        service = NewsService(test_db)
        article, is_new = service.add_article(
            url="https://example.com/article",
            title="Test Article",
            content="Content",
            summary="Summary",
            category="AI",
            source="Test",
            published_at=datetime.utcnow()
        )
        
        assert is_new == True
        assert article.title == "Test Article"
    
    def test_add_article_duplicate(self, test_db: Session, sample_news: News):
        """Test adding duplicate article."""
        from ai_news_aggregater.services.news_service import NewsService
        
        service = NewsService(test_db)
        article, is_new = service.add_article(
            url=sample_news.url,
            title="New Title",
            content="New content",
            summary="New summary",
            category="Tech",
            source="New Source",
            published_at=datetime.utcnow()
        )
        
        assert is_new == False
        assert article.id == sample_news.id
    
    def test_get_news_by_category(self, test_db: Session):
        """Test filtering by category."""
        from ai_news_aggregater.services.news_service import NewsService
        
        service = NewsService(test_db)
        
        # Add articles
        service.add_article(
            url="https://example.com/1",
            title="AI Article",
            content="Content",
            summary="Summary",
            category="AI",
            source="Test",
            published_at=datetime.utcnow()
        )
        service.add_article(
            url="https://example.com/2",
            title="Tech Article",
            content="Content",
            summary="Summary",
            category="Technology",
            source="Test",
            published_at=datetime.utcnow()
        )
        
        ai_articles = service.get_news_by_category("AI")
        assert len(ai_articles) == 1
        assert ai_articles[0].category == "AI"


class TestUserService:
    """Test user service operations."""
    
    def test_register_user_new(self, test_db: Session):
        """Test registering new user."""
        from ai_news_aggregater.services.news_service import UserService
        
        service = UserService(test_db)
        user, is_new = service.register_user(
            email="newuser@example.com",
            name="New User",
            interests=["AI"]
        )
        
        assert is_new == True
        assert user.email == "newuser@example.com"
    
    def test_register_user_duplicate(self, test_db: Session, sample_user: User):
        """Test registering duplicate user."""
        from ai_news_aggregater.services.news_service import UserService
        
        service = UserService(test_db)
        user, is_new = service.register_user(
            email=sample_user.email,
            name="Different Name",
            interests=["Different"]
        )
        
        assert is_new == False
        assert user.id == sample_user.id
        assert user.name == sample_user.name  # Original name preserved
    
    def test_register_user_invalid_email(self, test_db: Session):
        """Test invalid email validation."""
        from ai_news_aggregater.services.news_service import UserService
        
        service = UserService(test_db)
        
        with pytest.raises(ValueError):
            service.register_user(
                email="invalid-email",
                name="User",
                interests=["AI"]
            )


class TestValidators:
    """Test validation utilities."""
    
    def test_email_validation(self):
        """Test email format validation."""
        from ai_news_aggregater.utils.validators import Validators
        
        assert Validators.is_valid_email("test@example.com") == True
        assert Validators.is_valid_email("invalid-email") == False
        assert Validators.is_valid_email("@example.com") == False
    
    def test_url_validation(self):
        """Test URL format validation."""
        from ai_news_aggregater.utils.validators import Validators
        
        assert Validators.is_valid_url("https://example.com") == True
        assert Validators.is_valid_url("http://example.com/path") == True
        assert Validators.is_valid_url("invalid") == False
    
    def test_hour_validation(self):
        """Test hour range validation."""
        from ai_news_aggregater.utils.validators import Validators
        
        assert Validators.is_valid_hour(8) == True
        assert Validators.is_valid_hour(0) == True
        assert Validators.is_valid_hour(23) == True
        assert Validators.is_valid_hour(24) == False
        assert Validators.is_valid_hour(-1) == False


class TestTextHelpers:
    """Test text utility functions."""
    
    def test_truncate(self):
        """Test text truncation."""
        from ai_news_aggregater.utils.validators import TextHelpers
        
        text = "This is a long text that should be truncated"
        result = TextHelpers.truncate(text, max_length=20)
        
        assert len(result) <= 20
        assert result.endswith("...")
    
    def test_reading_time_estimate(self):
        """Test reading time estimation."""
        from ai_news_aggregater.utils.validators import TextHelpers
        
        text = " ".join(["word"] * 500)  # 500 words
        minutes = TextHelpers.estimate_reading_time(text, words_per_minute=200)
        
        assert minutes >= 2  # 500 words / 200 wpm = 2.5 minutes
