from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from ai_news_aggregater.models import News, User
from ai_news_aggregater.models.news import NewsType


class NewsService:

    @staticmethod
    def create_news(
        db: Session,
        title: str,
        content: str,
        summary: str,
        category: str,
        source: str,
        url: str,
        published_at: datetime,
        news_type: NewsType,
        fetch_hour: int = None,
        fetch_date: datetime = None
    ) -> Optional[News]:

        # Check existing news by URL
        existing_news = db.query(News).filter(News.url == url).first()

        if existing_news:
            return existing_news

        news = News(
            title=title,
            content=content,
            summary=summary,
            category=category,
            source=source,
            url=url,
            published_at=published_at,
            news_type=news_type,
            fetch_hour=fetch_hour or datetime.utcnow().hour,
            fetch_date=fetch_date or datetime.utcnow()
        )

        db.add(news)
        db.commit()
        db.refresh(news)

        return news

    @staticmethod
    def get_news_by_category(db: Session, category: str) -> List[News]:
        return db.query(News).filter(News.category == category).all()

    @staticmethod
    def get_news_by_hour(db: Session, hour: int) -> List[News]:
        return db.query(News).filter(News.fetch_hour == hour).all()

    @staticmethod
    def get_all_news(db: Session) -> List[News]:
        return db.query(News).all()


class UserService:

    @staticmethod
    def create_user(
        db: Session,
        name: str,
        email: str,
        interests: List[str]
    ) -> Optional[User]:

        # Check existing user by email
        existing_user = db.query(User).filter(User.email == email).first()

        if existing_user:
            return existing_user

        user = User(
            name=name,
            email=email,
            interests=interests,
            digest_subscribed=True,
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        return user

    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        return db.query(User).filter(User.email == email).first()

    @staticmethod
    def get_users_by_interest(db: Session, interest: str) -> List[User]:
        return db.query(User).filter(
            User.interests.contains([interest])
        ).all()