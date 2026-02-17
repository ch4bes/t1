#!/usr/bin/env python3
"""
Main entry point for the Weather Forecast Tracker CLI.
Run with: python run.py <command> [args]
"""
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from scripts.cli import main

if __name__ == "__main__":
    main()
