#!/usr/bin/env python3
"""Entry point for running the AI News Aggregator."""

import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from app.main import main

if __name__ == "__main__":
    main()
