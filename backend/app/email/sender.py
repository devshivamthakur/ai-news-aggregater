from datetime import datetime
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from app.config.settings import settings
from app.logging.logger import logger


class EmailSender:
    """Send personalized news digest emails via the Brevo API."""

    def __init__(self):
        """Initialize email sender with template loader."""
        template_dir = Path(__file__).parent / "templates"
        self.env = Environment(loader=FileSystemLoader(str(template_dir)))
        self.from_email = settings.brevo.sender_email or settings.admin_email

    def render_template(self, template_name: str, **context) -> str:
        """Render Jinja2 template with context variables."""
        try:
            template = self.env.get_template(template_name)
            return template.render(**context)
        except Exception as e:
            logger.error(f"Failed to render template {template_name}: {e}")
            raise

    def send_email_brevo(self, to_email: str, subject: str, body: str, is_html: bool = True) -> bool:
        """Send email using the Brevo transactional email API.

        Uses ``settings.brevo.sender_email`` (falling back to ``settings.admin_email``)
        as the verified sender address. Requires ``BREVO_API_KEY`` to be configured.

        Args:
            to_email: Recipient email address
            subject: Email subject
            body: Email body (HTML or text)
            is_html: Whether body is HTML

        Returns:
            True if successful, False otherwise
        """
        try:
            from brevo import Brevo
            from brevo.core.api_error import ApiError
            from brevo.transactional_emails import (
                SendTransacEmailRequestSender,
                SendTransacEmailRequestToItem,
            )

            if not settings.brevo.api_key:
                logger.error("BREVO_API_KEY is not configured; cannot send via Brevo")
                return False

            client = Brevo(api_key=settings.brevo.api_key)
            sender_email = settings.brevo.sender_email or settings.admin_email
            sender = SendTransacEmailRequestSender(
                email=sender_email, name=settings.brevo.sender_name
            )

            client.transactional_emails.send_transac_email(
                subject=subject,
                html_content=body if is_html else None,
                text_content=None if is_html else body,
                sender=sender,
                to=[SendTransacEmailRequestToItem(email=to_email)],
            )

            logger.info(f"Email sent successfully to {to_email} via Brevo")
            return True
        except ApiError as e:
            logger.error(f"Failed to send email via Brevo (API error {e.status_code}): {e}")
            return False
        except Exception as e:
            logger.error(f"Failed to send email via Brevo: {e}")
            return False

    def send_email(self, to_email: str, subject: str, body: str, is_html: bool = True) -> bool:
        """Send an email via the Brevo API.

        Args:
            to_email: Recipient email address
            subject: Email subject
            body: Email body (HTML or text)
            is_html: Whether body is HTML

        Returns:
            True if successful, False otherwise
        """
        return self.send_email_brevo(to_email, subject, body, is_html)

    def build_digest_articles(self, news_items: list, user_interests: list[str]) -> list[dict]:
        """Filter news items to a user's interests and serialize for the template.

        Args:
            news_items: Iterable of News ORM objects (or objects with the
                expected attributes).
            user_interests: List of category strings the user is interested in.

            Returns:
                List of article dicts matching the user's interests. If the user
                has no interests, all items are returned (unfiltered).
        """
        articles: list[dict] = []
        for news_item in news_items:
            category = getattr(news_item, "category", None)
            if user_interests and category not in user_interests:
                continue
            news_type = getattr(news_item, "news_type", None)
            articles.append(
                {
                    "title": news_item.title,
                    "summary": news_item.summary,
                    "url": news_item.url,
                    "category": category,
                    "source": getattr(news_item, "source", "Unknown"),
                    "news_type": news_type.value if hasattr(news_type, "value") else str(news_type),
                }
            )
        return articles

    def send_news_digest(self, user_email: str, user_name: str, articles: list[dict],
                        user_interests: list[str], unsubscribe_url: str = "",
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

            self.send_email(user_email, subject, html_body, is_html=True)

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
