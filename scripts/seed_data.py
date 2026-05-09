#!/usr/bin/env python3
"""Seed initial data."""

from ai_news_aggregater.storage.db import get_db
# from ai_news_aggregater.storage.crud import create_user

def seed_users():
    db = next(get_db())
    # create_user(db, "My Local Traveler", "mylocaltraveler@gmail.com", ["AI breakthroughs", "ethics"])
    # db.close()

if __name__ == "__main__":
    seed_users()