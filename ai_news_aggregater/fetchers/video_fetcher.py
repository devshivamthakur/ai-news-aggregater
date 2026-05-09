from datetime import datetime, timedelta, timezone
from typing import List, Optional
import os
import feedparser
from pydantic import BaseModel
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound
from ai_news_aggregater.logging.logger import logger
from ai_news_aggregater.fetchers.models import Transcript, ChannelVideo

class YouTubeScraper:
    """Scrape YouTube channels and fetch video transcripts."""
    
    def __init__(self):
        """Initialize YouTube scraper with optional proxy configuration."""
        proxy_config = None
        proxy_username = os.getenv("WEBSHARE_USERNAME")
        proxy_password = os.getenv("WEBSHARE_PASSWORD")

        if proxy_username and proxy_password:
            try:
                from youtube_transcript_api.proxies import WebshareProxyConfig
                proxy_config = WebshareProxyConfig(
                    proxy_username=proxy_username,
                    proxy_password=proxy_password
                )
                logger.info("YouTube scraper initialized with WebShare proxy")
            except Exception as e:
                logger.warning(f"Failed to initialize proxy: {e}")

        self.transcript_api = YouTubeTranscriptApi(proxy_config=proxy_config)

    def _get_rss_url(self, channel_id: str) -> str:
        """Get RSS feed URL for a YouTube channel."""
        return f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"

    def _extract_video_id(self, video_url: str) -> str:
        """Extract video ID from YouTube URL."""
        if "youtube.com/watch?v=" in video_url:
            return video_url.split("v=")[1].split("&")[0]
        if "youtube.com/shorts/" in video_url:
            return video_url.split("shorts/")[1].split("?")[0]
        if "youtu.be/" in video_url:
            return video_url.split("youtu.be/")[1].split("?")[0]
        return video_url

    def get_transcript(self, video_id: str) -> Optional[Transcript]:
        """Fetch transcript from a YouTube video.
        
        Args:
            video_id: YouTube video ID
            
        Returns:
            Transcript object if successful, None otherwise
        """
        try:
            logger.debug(f"Fetching transcript for video: {video_id}")
            transcript = self.transcript_api.fetch(video_id)
            text = " ".join([snippet.text for snippet in transcript])
            logger.debug(f"Successfully fetched transcript for {video_id}")
            return Transcript(text=text)
        except (TranscriptsDisabled, NoTranscriptFound):
            logger.debug(f"No transcript available for {video_id}")
            return None
        except Exception as e:
            logger.warning(f"Error fetching transcript for {video_id}: {e}")
            return None

    def get_latest_videos(self, channel_id: str, hours: int = 24) -> List[ChannelVideo]:
        """Get latest videos from a YouTube channel.
        
        Args:
            channel_id: YouTube channel ID
            hours: Only return videos from last N hours (skips shorts)
            
        Returns:
            List of ChannelVideo objects
        """
        try:
            logger.info(f"Fetching latest videos from channel: {channel_id}")
            feed = feedparser.parse(self._get_rss_url(channel_id))
            
            if not feed.entries:
                logger.warning(f"No videos found for channel {channel_id}")
                return []

            cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)
            videos = []

            for entry in feed.entries:
                # Skip shorts
                if "/shorts/" in entry.link:
                    logger.debug(f"Skipping short: {entry.title}")
                    continue
                
                try:
                    published_time = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
                    if published_time >= cutoff_time:
                        video_id = self._extract_video_id(entry.link)
                        video = ChannelVideo(
                            title=entry.title,
                            url=entry.link,
                            video_id=video_id,
                            published_at=published_time,
                            description=entry.get("summary", ""),
                        )
                        videos.append(video)
                        logger.debug(f"Fetched video: {video.title[:50]}...")
                except Exception as e:
                    logger.warning(f"Error processing video entry: {e}")
                    continue

            logger.info(f"Retrieved {len(videos)} videos from {channel_id}")
            return videos
            
        except Exception as e:
            logger.error(f"Failed to fetch videos from {channel_id}: {e}")
            return []

    def scrape_channel(self, channel_id: str, hours: int = 150) -> List[ChannelVideo]:
        """Scrape channel videos and fetch transcripts.
        
        Args:
            channel_id: YouTube channel ID
            hours: Only process videos from last N hours
            
        Returns:
            List of ChannelVideo objects with transcripts
        """
        logger.info(f"Scraping channel {channel_id} with {hours} hour lookback")
        videos = self.get_latest_videos(channel_id, hours)
        
        result = []
        for video in videos:
            transcript = self.get_transcript(video.video_id)
            video_with_transcript = video.model_copy(
                update={"transcript": transcript.text if transcript else None}
            )
            result.append(video_with_transcript)
            logger.debug(f"Processed video with transcript: {video.title[:50]}...")

        logger.info(f"Scraped {len(result)} videos from channel {channel_id}")
        print(f"Scraped {len(result)} videos from channel {channel_id}")
        return result


# Initialize global scraper instance
youtube_scraper = YouTubeScraper()

if __name__ == "__main__":
    # Test fetching videos
    try:
        scraper = YouTubeScraper()
        
        # Example: Fetch single video transcript
        transcript = scraper.get_transcript("jqd6_bbjhS8")
        if transcript:
            print(f"Transcript: {transcript.text[:100]}...")
        
        # Example: Fetch channel videos
        channel_videos = scraper.scrape_channel(
            "UCn8ujwUInbJkBhffxqAPBVQ", hours=200
        )
        print(f"Fetched {channel_videos} videos with transcripts")
        
        logger.info("YouTube scraper initialized and ready")
    except Exception as e:
        logger.error(f"Error in YouTube scraper: {e}")