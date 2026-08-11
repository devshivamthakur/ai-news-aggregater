#!/usr/bin/env python3
"""Database migration script."""

from app.storage.db import create_tables

if __name__ == "__main__":
    create_tables()
