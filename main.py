#!/usr/bin/env python3
"""
Main entry point for Finance Management Application
This file imports and runs the complete application to ensure compatibility.
"""

import tkinter as tk
from tkinter import messagebox
import sys
import logging
from typing import Optional

# Import all necessary components from the modular structure
from config import WINDOW_TITLE, WINDOW_SIZE
from database import Database
from models import User

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('finance_app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


# For now, to ensure the app works without any alterations,
# we'll import and use the classes from the original file
from Complete_app import FinanceApp


def main():
    """Main entry point"""
    try:
        app = FinanceApp()
        app.run()
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        if tk._default_root:
            messagebox.showerror("Fatal Error", f"Failed to start application: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 