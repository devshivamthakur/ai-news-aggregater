from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Integer, JSON, String

from ai_news_aggregater.models.Base import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=True)
    password_hash = Column(String, nullable=True)
    interests = Column(JSON)  # List of categories, e.g., ["AI breakthroughs", "ethics"]
    digest_subscribed = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Integer, default=1)  # 1 for active, 0 for inactive
