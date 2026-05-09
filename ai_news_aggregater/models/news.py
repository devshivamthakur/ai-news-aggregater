from sqlalchemy import Column, Integer, String, Text, DateTime, Enum
from datetime import datetime
import enum
from ai_news_aggregater.models.Base import Base


class NewsType(enum.Enum):
    ARTICLE = "article"
    VIDEO = "video"
    BLOG_POST = "blog_post"

class News(Base):
    __tablename__ = "news"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content = Column(Text)
    summary = Column(Text)
    category = Column(String)  # e.g., AI breakthroughs, ethics
    source = Column(String)  # e.g., OpenAI blog, Medium
    url = Column(String, unique=True, nullable=False)
    published_at = Column(DateTime)
    news_type = Column(Enum(NewsType), default=NewsType.ARTICLE)
    fetch_hour = Column(Integer)  # Hour (0-23) when the news was fetched
    fetch_date = Column(DateTime)  # Date and time when the news was fetched
    created_at = Column(DateTime, default=datetime.utcnow)