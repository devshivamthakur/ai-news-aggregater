import requests
from bs4 import BeautifulSoup
from datetime import datetime
from typing import List, Optional
from ai_news_aggregater.utils.errors import FetchError, retry_on_failure
from ai_news_aggregater.logging.logger import logger
from ai_news_aggregater.fetchers.models import WebContent


class WebScraper:
    """Scrape and extract content from web pages."""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        self.timeout = 15
    
    @retry_on_failure(max_retries=3, delay=2.0)
    def fetch_content(self, url: str, source_name: str = "Web") -> Optional[WebContent]:
        """Fetch and parse content from a web URL."""
        try:
            response = requests.get(url, timeout=self.timeout, headers=self.headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract title
            title = None
            if soup.find('h1'):
                title = soup.find('h1').text.strip()
            elif soup.find('title'):
                title = soup.find('title').text.strip()
            title = title or "No Title"
            
            # Extract main content
            content_elem = soup.find('article') or soup.find('main') or soup.find('body')
            if content_elem:
                # Remove script and style elements
                for elem in content_elem(['script', 'style', 'nav']):
                    elem.decompose()
                content = content_elem.get_text(separator=' ', strip=True)
            else:
                content = soup.get_text(separator=' ', strip=True)
            
            # Limit content length
            content = content[:5000] if len(content) > 5000 else content
            
            return WebContent(
                title=title,
                content=content,
                url=url,
                published_at=datetime.utcnow(),
                source=source_name
            )
        except requests.RequestException as e:
            logger.error(f"Failed to fetch {url}: {e}")
            return None
        except Exception as e:
            logger.error(f"Error parsing {url}: {e}")
            return None
    
    def fetch_multiple(self, urls: List[str], source_name: str = "Web") -> List[WebContent]:
        """Fetch content from multiple URLs."""
        results = []
        for url in urls:
            content = self.fetch_content(url, source_name)
            if content:
                results.append(content)
        return results


# Initialize global scraper instance
web_scraper = WebScraper()

# Convenience functions for backward compatibility
def fetch_web_content(url: str, source_name: str = "Web") -> Optional[WebContent]:
    """Fetch content from a web URL."""
    return web_scraper.fetch_content(url, source_name)

def fetch_medium_post(url: str) -> Optional[WebContent]:
    """Fetch a Medium blog post."""
    return web_scraper.fetch_content(url, "Medium")

def fetch_website_content(url: str) -> Optional[WebContent]:
    """Fetch content from any website."""
    return web_scraper.fetch_content(url, "Web")


if __name__ == "__main__":
    # Test fetching web content
    try:
        scraper = WebScraper()
        content = scraper.fetch_content("https://example.com", "Example")
        if content:
            print(f"Title: {content.title}")
            print(f"Content length: {len(content.content)}")
        logger.info("Web scraper initialized and ready")
    except Exception as e:
        logger.error(f"Error in web scraper: {e}")