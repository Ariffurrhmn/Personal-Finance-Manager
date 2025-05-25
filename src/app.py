"""
Main application entry point for the Finance Management Application
"""

import tkinter as tk
import sys
import logging
from typing import Optional
try:
    from .config import WINDOW_SIZE, WINDOW_TITLE, WINDOW_ICON
    from .models import User
    from .database import Database, DatabaseError
    from .ui_login import LoginScreen, RegisterScreen
    from .ui_main import MainApp
except ImportError:
    from config import WINDOW_SIZE, WINDOW_TITLE, WINDOW_ICON
    from models import User
    from database import Database, DatabaseError
    from ui_login import LoginScreen, RegisterScreen
    from ui_main import MainApp

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

class FinanceApp:
    """Main application controller"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title(WINDOW_TITLE)
        self.root.geometry(WINDOW_SIZE)
        self.root.resizable(True, True)
        
        # Set window icon
        try:
            self.root.iconbitmap(WINDOW_ICON)
        except Exception as e:
            logger.warning(f"Could not load window icon: {e}")
        
        # Initialize database
        try:
            self.database = Database()
            logger.info("Database initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            tk.messagebox.showerror("Database Error", 
                                   f"Failed to initialize database: {e}")
            sys.exit(1)
        
        # Current user and UI components
        self.current_user: Optional[User] = None
        self.current_screen = None
        
        # Set up window close handler
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Start with login screen
        self.show_login_screen()
    
    def show_login_screen(self):
        """Show the login screen"""
        try:
            logger.info("Showing login screen")
            self.current_screen = LoginScreen(
                parent=self.root,
                database=self.database,
                on_login_success=self.on_login_success,
                on_show_register=self.show_register_screen
            )
        except Exception as e:
            logger.error(f"Error showing login screen: {e}")
            tk.messagebox.showerror("Error", f"Failed to show login screen: {e}")
    
    def show_register_screen(self):
        """Show the registration screen"""
        try:
            logger.info("Showing register screen")
            self.current_screen = RegisterScreen(
                parent=self.root,
                database=self.database,
                on_register_success=self.show_login_screen,
                on_show_login=self.show_login_screen
            )
        except Exception as e:
            logger.error(f"Error showing register screen: {e}")
            tk.messagebox.showerror("Error", f"Failed to show register screen: {e}")
    
    def on_login_success(self, user: User):
        """Handle successful login"""
        try:
            logger.info(f"User {user.email} logged in successfully")
            self.current_user = user
            self.show_main_app()
        except Exception as e:
            logger.error(f"Error handling login success: {e}")
            tk.messagebox.showerror("Error", f"Failed to load main application: {e}")
    
    def show_main_app(self):
        """Show the main application"""
        try:
            logger.info("Showing main application")
            self.current_screen = MainApp(
                parent=self.root,
                database=self.database,
                user=self.current_user,
                on_logout=self.on_logout
            )
        except Exception as e:
            logger.error(f"Error showing main app: {e}")
            tk.messagebox.showerror("Error", f"Failed to load main application: {e}")
    
    def on_logout(self):
        """Handle user logout"""
        try:
            logger.info(f"User {self.current_user.email if self.current_user else 'Unknown'} logged out")
            self.current_user = None
            self.show_login_screen()
        except Exception as e:
            logger.error(f"Error handling logout: {e}")
            tk.messagebox.showerror("Error", f"Failed to logout: {e}")
    
    def on_closing(self):
        """Handle application closing"""
        try:
            logger.info("Application closing")
            if self.current_user:
                logger.info(f"User {self.current_user.email} session ending")
            
            # Close database connection
            if hasattr(self.database, 'close'):
                self.database.close()
            
            # Destroy the window
            self.root.destroy()
            
        except Exception as e:
            logger.error(f"Error during application closing: {e}")
        finally:
            sys.exit(0)
    
    def run(self):
        """Start the application"""
        try:
            logger.info("Starting Finance Management Application")
            self.root.mainloop()
        except KeyboardInterrupt:
            logger.info("Application interrupted by user")
            self.on_closing()
        except Exception as e:
            logger.error(f"Unexpected error in main loop: {e}")
            tk.messagebox.showerror("Fatal Error", 
                                   f"An unexpected error occurred: {e}")
            sys.exit(1)

def main():
    """Main entry point"""
    try:
        app = FinanceApp()
        app.run()
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        if tk._default_root:
            tk.messagebox.showerror("Fatal Error", 
                                   f"Failed to start application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 