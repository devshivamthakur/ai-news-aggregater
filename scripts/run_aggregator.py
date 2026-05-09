#!/usr/bin/env python3
"""Entry point for running the AI News Aggregator."""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from ai_news_aggregater.main import main

if __name__ == "__main__":
    main()