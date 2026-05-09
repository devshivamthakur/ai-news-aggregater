#!/usr/bin/env python3
"""Database migration script."""

from ai_news_aggregater.storage.db import create_tables

if __name__ == "__main__":
    create_tables()