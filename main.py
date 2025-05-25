#!/usr/bin/env python3
"""
Finance Management Application - Main Launcher

This is the main entry point for the Finance Management Application.
Run this file to start the application.

Usage:
    python main.py
"""

import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

if __name__ == "__main__":
    try:
        from app import main
        main()
    except KeyboardInterrupt:
        print("\nApplication interrupted by user.")
        sys.exit(0)
    except Exception as e:
        print(f"Failed to start application: {e}")
        sys.exit(1) 