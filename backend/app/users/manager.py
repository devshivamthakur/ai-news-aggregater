from app.logging.logger import logger


def add_user(email: str, interests: list):
    """Add a new user."""
    # Assume db session is handled elsewhere
    logger.info(f"Adding user {email} with interests {interests}")
    # In practice, get db and call create_user

def get_user_interests(email: str) -> list:
    """Get user interests."""
    # Placeholder
    return ["AI breakthroughs"]
