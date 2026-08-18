import os
import socket
from datetime import UTC, datetime, timedelta

import feedparser
import yt_dlp
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import NoTranscriptFound, TranscriptsDisabled

from app.config.settings import settings
from app.fetchers.models import ChannelVideo, Transcript
from app.logging.logger import logger


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
        self.ydl = yt_dlp.YoutubeDL(
            {
                "quiet": True,
                "no_warnings": True,
                "extract_flat": True,
                "force_generic_extractor": True,
            }
        )


    def _extract_video_id(self, video_url: str) -> str:
        """Extract video ID from YouTube URL."""
        if "youtube.com/watch?v=" in video_url:
            return video_url.split("v=")[1].split("&")[0]
        if "youtube.com/shorts/" in video_url:
            return video_url.split("shorts/")[1].split("?")[0]
        if "youtu.be/" in video_url:
            return video_url.split("youtu.be/")[1].split("?")[0]
        return video_url

    def get_transcript(self, video_id: str) -> Transcript | None:
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

    def get_latest_videos(self, channel_id: str, hours: int = 24) -> list[ChannelVideo]:
        """Get latest videos from a YouTube channel.

        Args:
            channel_id: YouTube channel ID
            hours: Only return videos from last N hours (skips shorts)

        Returns:
            List of ChannelVideo objects
        """
        try:
            logger.info(f"Fetching latest videos from channel: {channel_id}")
            socket.setdefaulttimeout(settings.fetcher.timeout)
            
            playlist_url = f"https://www.youtube.com/channel/{channel_id}/videos"
            result = self.ydl.extract_info(playlist_url, download=False)

            if not result or "entries" not in result:
                logger.warning(f"No videos found for channel {channel_id}")
                return []

            cutoff_time = datetime.now(UTC) - timedelta(hours=hours)
            videos = []

            for entry in result["entries"]:
                published_at = datetime.fromtimestamp(entry.get("timestamp", 0), tz=UTC)
                if published_at < cutoff_time:
                    continue
                
                # Skip shorts, yt-dlp may not always have a clear flag
                if "shorts" in entry.get("title", "").lower() or "/shorts/" in entry.get("url", ""):
                    logger.debug(f"Skipping short: {entry.get('title')}")
                    continue
                
                videos.append(
                    ChannelVideo(
                        video_id=entry["id"],
                        title=entry["title"],
                        description=entry.get("description", ""),
                        published_at=published_at,
                        url=f"https://www.youtube.com/watch?v={entry['id']}",
                        thumbnail_url=entry.get("thumbnail"),
                        source_id=channel_id,
                    )
                )
            
            return videos
        
        except Exception as e:
            logger.error(
                "Failed to fetch videos for channel %s: %s",
                channel_id,
                e,
            )
            return []

    def get_videos_via_rss(self, channel_id: str, hours: int = 24) -> list[ChannelVideo]:
        """Get latest videos from a YouTube channel via its RSS feed.

        Args:
            channel_id: YouTube channel ID
            hours: Only return videos from last N hours (skips shorts)

        Returns:
            List of ChannelVideo objects
        """
        try:
            logger.info(f"Fetching latest videos (RSS) from channel: {channel_id}")
            socket.setdefaulttimeout(settings.fetcher.timeout)
            feed = feedparser.parse(
                f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
            )

            if not feed.entries:
                logger.warning(f"No videos found for channel {channel_id}")
                return []

            cutoff_time = datetime.now(UTC) - timedelta(hours=hours)
            videos = []

            for entry in feed.entries:
                # Skip shorts
                if "/shorts/" in entry.link:
                    logger.debug(f"Skipping short: {entry.title}")
                    continue

                try:
                    published_time = datetime(*entry.published_parsed[:6], tzinfo=UTC)
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

    def scrape_channel(self, channel_id: str, hours: int = 150) -> list[ChannelVideo]:
        """Scrape channel videos and fetch transcripts concurrently.

        Args:
            channel_id: YouTube channel ID
            hours: Only process videos from last N hours

        Returns:
            List of ChannelVideo objects with transcripts
        """
        logger.info(f"Scraping channel {channel_id} with {hours} hour lookback")
        videos = self.get_latest_videos(channel_id, hours)

        if not videos:
            return []

        # Fetch transcripts concurrently using ThreadPoolExecutor
        from concurrent.futures import ThreadPoolExecutor, as_completed

        result = []
        with ThreadPoolExecutor(max_workers=5) as executor:
            future_to_video = {
                executor.submit(self.get_transcript, video.video_id): video
                for video in videos
            }
            for future in as_completed(future_to_video):
                video = future_to_video[future]
                try:
                    transcript = future.result()
                    video_with_transcript = video.model_copy(
                        update={"transcript": transcript.text if transcript else None}
                    )
                    result.append(video_with_transcript)
                except Exception as e:
                    logger.warning(f"Error fetching transcript for {video.video_id}: {e}")
                    result.append(video)

        logger.info(f"Scraped {len(result)} videos from channel {channel_id}")
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
