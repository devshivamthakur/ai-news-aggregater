import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
from jinja2 import Environment, FileSystemLoader
from ai_news_aggregater.config.settings import settings
from ai_news_aggregater.logging.logger import logger


class EmailSender:
    """Send personalized news digest emails."""
    
    def __init__(self):
        """Initialize email sender with template loader."""
        template_dir = Path(__file__).parent / "templates"
        self.env = Environment(loader=FileSystemLoader(str(template_dir)))
        self.from_email = settings.smtp_username
    
    def render_template(self, template_name: str, **context) -> str:
        """Render Jinja2 template with context variables."""
        try:
            template = self.env.get_template(template_name)
            return template.render(**context)
        except Exception as e:
            logger.error(f"Failed to render template {template_name}: {e}")
            raise
    
    def send_email_smtp(self, to_email: str, subject: str, body: str, is_html: bool = True) -> bool:
        """Send email using SMTP.
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            body: Email body (HTML or text)
            is_html: Whether body is HTML
            
        Returns:
            True if successful, False otherwise
        """
        try:
            msg = MIMEMultipart('alternative')
            msg['From'] = self.from_email
            msg['To'] = to_email
            msg['Subject'] = subject
            
            mime_type = 'html' if is_html else 'plain'
            msg.attach(MIMEText(body, mime_type))

            server = smtplib.SMTP(settings.smtp_server, settings.smtp_port)
            server.starttls()
            server.login(settings.smtp_username, settings.smtp_password)
            server.sendmail(self.from_email, to_email, msg.as_string())
            server.quit()
            
            logger.info(f"Email sent successfully to {to_email}")
            return True
        except Exception as e:
            logger.error(f"Failed to send email via SMTP: {e}")
            return False
    
    def send_news_digest(self, user_email: str, user_name: str, articles: List[Dict], 
                        user_interests: List[str], unsubscribe_url: str = "", 
                        preferences_url: str = "") -> bool:
        """Send personalized news digest email.
        
        Args:
            user_email: User email address
            user_name: User display name
            articles: List of article dictionaries
            user_interests: List of user interests
            unsubscribe_url: URL for unsubscribing
            preferences_url: URL for managing preferences
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Calculate digest context
            articles_count = len(articles)
            sources = set(article.get('source', 'Unknown') for article in articles)
            sources_count = len(sources)
            
            # Estimate total reading time (average 250 words per minute)
            total_words = sum(len(article.get('summary', '').split()) for article in articles)
            total_reading_time = max(1, total_words // 250)
            
            # Prepare context for template
            context = {
                'user_name': user_name,
                'digest_date': datetime.now().strftime('%B %d, %Y'),
                'timezone': 'UTC',
                'articles': articles,
                'articles_count': articles_count,
                'sources_count': sources_count,
                'total_reading_time': total_reading_time,
                'user_interests': user_interests,
                'unsubscribe_url': unsubscribe_url,
                'preferences_url': preferences_url,
            }
            
            # Render template
            html_body = self.render_template('news_digest.html', **context)
            
            subject = f"AIPulse Digest — {context['digest_date']}"
            
            self.send_email_smtp(user_email, subject, html_body, is_html=True)
                
        except Exception as e:
            logger.error(f"Failed to send news digest to {user_email}: {e}")
            return False


# Initialize global email sender instance
email_sender = EmailSender()


# # Convenience functions
# def send_news_email(user_email: str, user_name: str, articles: List[Dict], 
#                    user_interests: List[str], **kwargs) -> bool:
#     """Send personalized news digest email."""
#     return email_sender.send_news_digest(
#         user_email=user_email,
#         user_name=user_name,
#         articles=articles,
#         user_interests=user_interests,
#         **kwargs
#     )


# if __name__ == "__main__":
#     # Test email sending
#     test_articles = [
#         {
#             'title': 'OpenAI Announces GPT-5',
#             'summary': 'OpenAI has announced the latest version of its language model.',
#             'url': 'https://example.com/article1',
#             'source': 'OpenAI Blog',
#             'category': 'AI Breakthroughs',
#             'reading_time_minutes': 5
#         },
#         {
#             'title': 'Anthropic Releases Claude 4',
#             'summary': 'Anthropic released a new version of its AI assistant Claude.',
#             'url': 'https://example.com/article2',
#             'source': 'Anthropic Blog',
#             'category': 'AI Breakthroughs',
#             'reading_time_minutes': 3
#         }
#     ]
    
#     # Test sending
#     success = send_news_email(
#         user_email="mylocaltraveler@gmail.com",
#         user_name="Test User",
#         articles=test_articles,
#         user_interests=["AI Breakthroughs", "Research"]
#     )
    
#     if success:
#         logger.info("Test email sent successfully!")
#     else:
#         logger.error("Test email failed to send.")
