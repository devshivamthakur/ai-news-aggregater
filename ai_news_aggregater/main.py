import asyncio
from datetime import datetime
from ai_news_aggregater.storage.db import SessionLocal
from ai_news_aggregater.storage.crud import NewsService
from ai_news_aggregater.processors.ContentAnalyzer import ContentAnalyzerInstance
from ai_news_aggregater.email.sender import email_sender
from ai_news_aggregater.logging.logger import logger
from ai_news_aggregater.config.settings import settings
from ai_news_aggregater.models import NewsType
from ai_news_aggregater.utils.utils import BLOG_FEEDS, YOUTUBE_CHANNELS
from ai_news_aggregater.fetchers.blog_fetcher import rss_scraper
from ai_news_aggregater.fetchers.video_fetcher import youtube_scraper
from dotenv import load_dotenv
load_dotenv()

async def aggregate_and_email():
    """Main function to fetch news, process, store, and send emails."""
    db = SessionLocal()
    try:
        current_hour = datetime.utcnow().hour
        current_time = datetime.utcnow()
        
        logger.info(f"Starting news aggregation at hour {current_hour:02d}:00 UTC")
        
        # Fetch news from various sources
        all_news = []
        
        try:
            logger.info("Fetching blog posts...")
            openai_posts = rss_scraper.fetch_multiple_feeds(BLOG_FEEDS, hours=24)
            all_news.extend(openai_posts)
            logger.info(f"Fetched {len(openai_posts)} blog posts")
        except Exception as e:
            logger.error(f"Failed to fetch blog posts: {e}")

        try:
            logger.info("Fetching YouTube videos...")
            for channel_id in YOUTUBE_CHANNELS:
                channel_videos = youtube_scraper.scrape_channel(channel_id, hours=24)
                all_news.extend(channel_videos)
        except Exception as e:
            logger.error(f"Failed to fetch YouTube videos: {e}")    
        
        logger.info(f"Fetched {len(all_news)} news items")
        
        # Process and store news
        stored_news = []
        for news_item in all_news:
            try:
                result = await ContentAnalyzerInstance.process_content(
                    title=news_item.title,
                    content=news_item.content if hasattr(news_item, 'content') else news_item.description,
                )
                news_record = NewsService.create_news(
                    db=db,
                    title=news_item.title,
                    content=news_item.content if hasattr(news_item, 'content') else news_item.description,
                    summary=result.summary if result else '',
                    category=result.category if result else '',
                    source=news_item.source if hasattr(news_item, 'source') else 'Unknown',
                    url=news_item.url if hasattr(news_item, 'url') else '',
                    published_at=news_item.published_at if hasattr(news_item, 'published_at') else datetime.utcnow(),
                    news_type=NewsType.VIDEO if news_item.source and news_item.source == 'YouTube' else NewsType.ARTICLE,
                    fetch_hour=current_hour,
                    fetch_date=current_time
                )
                if news_record:
                    stored_news.append(news_record)
                    logger.info(f"Stored news: {news_record.title[:50]}...")
            except Exception as e:
                logger.error(f"Failed to process news: {e}")
        
        logger.info(f"Stored {len(stored_news)} news items")
        
        # Get all users and send personalized emails
        from ai_news_aggregater.models import User
        users = db.query(User).all()
        
        for user in users:
            try:
                user_interests = user.interests or []
                user_news = []
                
                # Filter news by user interests
                for news_item in stored_news:
                    if news_item.category in user_interests or not user_interests:
                        user_news.append({
                            'title': news_item.title,
                            'summary': news_item.summary,
                            'url': news_item.url,
                            'category': news_item.category,
                            'source': news_item.source,
                            "news_type": news_item.news_type.value
                        })
                
                if user_news:
                    logger.info(f"Sending {len(user_news)} news items to {user.email}")
                    email_sender.send_news_digest(
                        user_email=user.email,
                        user_name=user.name or user.email.split('@')[0],
                        articles=user_news,
                        user_interests=user_interests,
                       
                    )
                else:
                    logger.info(f"No matching news for user {user.email}")
                    
            except Exception as e:
                logger.error(f"Failed to send email to {user.email}: {e}")
        
        logger.info("News aggregation completed successfully")
        
    except Exception as e:
        logger.error(f"Failed to aggregate and email news: {e}")
    finally:
        db.close()

def main():
    """Entry point for the aggregator."""
    logger.info(f"AI News Aggregator starting...")
    logger.info(f"Configured fetch hour: {settings.custom_fetch_hour} (24-hour format)")
    
    # For testing/manual run
    asyncio.run(aggregate_and_email())

if __name__ == "__main__":
    main()
