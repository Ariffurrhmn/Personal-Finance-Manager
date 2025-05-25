"""
Login and Registration UI components
"""

import tkinter as tk
from tkinter import messagebox
from typing import Callable, Optional
try:
    from .config import COLORS, FONTS, APP_LOGO
    from .models import User, ValidationError
    from .database import Database, DatabaseError
except ImportError:
    from config import COLORS, FONTS, APP_LOGO
    from models import User, ValidationError
    from database import Database, DatabaseError

class LoginScreen:
    """Login screen UI component"""
    
    def __init__(self, parent: tk.Tk, database: Database, 
                 on_login_success: Callable[[User], None],
                 on_show_register: Callable[[], None]):
        self.parent = parent
        self.database = database
        self.on_login_success = on_login_success
        self.on_show_register = on_show_register
        
        self.email_var = tk.StringVar()
        self.password_var = tk.StringVar()
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the login screen UI"""
        # Clear the window
        for widget in self.parent.winfo_children():
            widget.destroy()
        
        # Create main container
        main_frame = tk.Frame(self.parent, bg=COLORS['LIGHT_GREY'])
        main_frame.pack(fill='both', expand=True)
        
        # Black header section
        header_frame = tk.Frame(main_frame, bg=COLORS['BLACK'], height=200)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)
        
        # Create a container for icon and title
        header_container = tk.Frame(header_frame, bg=COLORS['BLACK'])
        header_container.pack(expand=True)
        
        # Try to load and display icon
        try:
            import os
            if os.path.exists(APP_LOGO):
                # Load icon image
                icon_image = tk.PhotoImage(file=APP_LOGO)
                # Resize if needed (for ICO files, we might need to adjust)
                icon_label = tk.Label(header_container, image=icon_image, 
                                    bg=COLORS['BLACK'])
                icon_label.image = icon_image  # Keep a reference
                icon_label.pack(pady=(20, 10))
        except Exception:
            # If icon loading fails, just continue without it
            pass
        
        # Title in header
        title_label = tk.Label(header_container, text="Finance Manager", 
                              font=FONTS['LOGIN_TITLE'], 
                              fg=COLORS['WHITE'], 
                              bg=COLORS['BLACK'])
        title_label.pack(pady=(0, 20))
        
        # Body section
        body_frame = tk.Frame(main_frame, bg=COLORS['LIGHT_GREY'])
        body_frame.pack(fill='both', expand=True, padx=50, pady=30)
        
        # Email entry
        self.email_entry = tk.Entry(body_frame, textvariable=self.email_var, 
                                   font=FONTS['LOGIN_INPUT'], 
                                   relief='solid', bd=2, bg=COLORS['WHITE'])
        self.email_entry.insert(0, "Email")
        self.email_entry.pack(fill='x', pady=(0, 15), ipady=10)
        
        # Password entry
        self.password_entry = tk.Entry(body_frame, textvariable=self.password_var, 
                                      font=FONTS['LOGIN_INPUT'], 
                                      show="*", relief='solid', bd=2, bg=COLORS['WHITE'])
        self.password_entry.insert(0, "Password")
        self.password_entry.pack(fill='x', pady=(0, 20), ipady=10)
        
        # Bind focus events to clear placeholder text
        self.email_entry.bind("<FocusIn>", self._clear_email_placeholder)
        self.password_entry.bind("<FocusIn>", self._clear_password_placeholder)
        
        # Bind Enter key to login
        self.email_entry.bind("<Return>", lambda e: self.login())
        self.password_entry.bind("<Return>", lambda e: self.login())
        
        # Login button
        login_btn = tk.Button(body_frame, text="Login", 
                             font=FONTS['LOGIN_BUTTON'], 
                             bg=COLORS['CYAN_GREEN'], fg=COLORS['BLACK'], 
                             command=self.login, relief='flat', bd=0)
        login_btn.pack(fill='x', pady=(0, 15), ipady=15)
        
        # Register button
        register_btn = tk.Button(body_frame, text="Register", 
                                font=FONTS['LOGIN_BUTTON'], 
                                bg=COLORS['DARK_GREY'], fg=COLORS['BLACK'], 
                                command=self.on_show_register, relief='flat', bd=0)
        register_btn.pack(fill='x', ipady=15)
        
        # Set focus to email entry
        self.email_entry.focus()
    
    def _clear_email_placeholder(self, event):
        """Clear email placeholder text on focus"""
        if self.email_entry.get() == "Email":
            self.email_entry.delete(0, tk.END)
    
    def _clear_password_placeholder(self, event):
        """Clear password placeholder text on focus"""
        if self.password_entry.get() == "Password":
            self.password_entry.delete(0, tk.END)
            self.password_entry.config(show="*")
    
    def login(self):
        """Handle login attempt"""
        email = self.email_var.get().strip()
        password = self.password_var.get().strip()
        
        # Validate input
        if email == "Email" or not email:
            messagebox.showerror("Error", "Please enter your email")
            self.email_entry.focus()
            return
        
        if password == "Password" or not password:
            messagebox.showerror("Error", "Please enter your password")
            self.password_entry.focus()
            return
        
        try:
            # Attempt authentication
            user = self.database.authenticate_user(email, password)
            if user:
                self.on_login_success(user)
            else:
                messagebox.showerror("Login Failed", "Invalid email or password")
                self.password_entry.delete(0, tk.END)
                self.password_entry.insert(0, "Password")
                self.password_entry.config(show="")
                self.email_entry.focus()
        
        except DatabaseError as e:
            messagebox.showerror("Database Error", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {e}")

class RegisterScreen:
    """Registration screen UI component"""
    
    def __init__(self, parent: tk.Tk, database: Database, 
                 on_register_success: Callable[[], None],
                 on_show_login: Callable[[], None]):
        self.parent = parent
        self.database = database
        self.on_register_success = on_register_success
        self.on_show_login = on_show_login
        
        self.name_var = tk.StringVar()
        self.email_var = tk.StringVar()
        self.password_var = tk.StringVar()
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the registration screen UI"""
        # Clear the window
        for widget in self.parent.winfo_children():
            widget.destroy()
        
        # Create main container
        main_frame = tk.Frame(self.parent, bg=COLORS['LIGHT_GREY'])
        main_frame.pack(fill='both', expand=True)
        
        # Black header section
        header_frame = tk.Frame(main_frame, bg=COLORS['BLACK'], height=200)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)
        
        # Create a container for icon and title
        header_container = tk.Frame(header_frame, bg=COLORS['BLACK'])
        header_container.pack(expand=True)
        
        # Try to load and display icon
        try:
            import os
            if os.path.exists(APP_LOGO):
                # Load icon image
                icon_image = tk.PhotoImage(file=APP_LOGO)
                # Resize if needed (for ICO files, we might need to adjust)
                icon_label = tk.Label(header_container, image=icon_image, 
                                    bg=COLORS['BLACK'])
                icon_label.image = icon_image  # Keep a reference
                icon_label.pack(pady=(20, 10))
        except Exception:
            # If icon loading fails, just continue without it
            pass
        
        # Title in header
        title_label = tk.Label(header_container, text="Finance Manager", 
                              font=FONTS['LOGIN_TITLE'], 
                              fg=COLORS['WHITE'], 
                              bg=COLORS['BLACK'])
        title_label.pack(pady=(0, 20))
        
        # Body section
        body_frame = tk.Frame(main_frame, bg=COLORS['LIGHT_GREY'])
        body_frame.pack(fill='both', expand=True, padx=50, pady=30)
        
        # Name entry
        self.name_entry = tk.Entry(body_frame, textvariable=self.name_var, 
                                  font=FONTS['LOGIN_INPUT'], 
                                  relief='solid', bd=2, bg=COLORS['WHITE'])
        self.name_entry.insert(0, "Name")
        self.name_entry.pack(fill='x', pady=(0, 15), ipady=10)
        
        # Email entry
        self.email_entry = tk.Entry(body_frame, textvariable=self.email_var, 
                                   font=FONTS['LOGIN_INPUT'], 
                                   relief='solid', bd=2, bg=COLORS['WHITE'])
        self.email_entry.insert(0, "Email")
        self.email_entry.pack(fill='x', pady=(0, 15), ipady=10)
        
        # Password entry
        self.password_entry = tk.Entry(body_frame, textvariable=self.password_var, 
                                      font=FONTS['LOGIN_INPUT'], 
                                      show="*", relief='solid', bd=2, bg=COLORS['WHITE'])
        self.password_entry.insert(0, "Password")
        self.password_entry.pack(fill='x', pady=(0, 20), ipady=10)
        
        # Bind focus events to clear placeholder text
        self.name_entry.bind("<FocusIn>", self._clear_name_placeholder)
        self.email_entry.bind("<FocusIn>", self._clear_email_placeholder)
        self.password_entry.bind("<FocusIn>", self._clear_password_placeholder)
        
        # Bind Enter key to register
        self.name_entry.bind("<Return>", lambda e: self.register())
        self.email_entry.bind("<Return>", lambda e: self.register())
        self.password_entry.bind("<Return>", lambda e: self.register())
        
        # Register button
        register_btn = tk.Button(body_frame, text="Create Account", 
                                font=FONTS['LOGIN_BUTTON'], 
                                bg=COLORS['CYAN_GREEN'], fg=COLORS['BLACK'], 
                                command=self.register, relief='flat', bd=0)
        register_btn.pack(fill='x', pady=(0, 15), ipady=15)
        
        # Back to login button
        back_btn = tk.Button(body_frame, text="Back to Login", 
                            font=FONTS['LOGIN_BUTTON'], 
                            bg=COLORS['DARK_GREY'], fg=COLORS['BLACK'], 
                            command=self.on_show_login, relief='flat', bd=0)
        back_btn.pack(fill='x', ipady=15)
        
        # Set focus to name entry
        self.name_entry.focus()
    
    def _clear_name_placeholder(self, event):
        """Clear name placeholder text on focus"""
        if self.name_entry.get() == "Name":
            self.name_entry.delete(0, tk.END)
    
    def _clear_email_placeholder(self, event):
        """Clear email placeholder text on focus"""
        if self.email_entry.get() == "Email":
            self.email_entry.delete(0, tk.END)
    
    def _clear_password_placeholder(self, event):
        """Clear password placeholder text on focus"""
        if self.password_entry.get() == "Password":
            self.password_entry.delete(0, tk.END)
            self.password_entry.config(show="*")
    
    def register(self):
        """Handle registration attempt"""
        name = self.name_var.get().strip()
        email = self.email_var.get().strip()
        password = self.password_var.get().strip()
        
        # Validate input
        if name == "Name" or not name:
            messagebox.showerror("Error", "Please enter your name")
            self.name_entry.focus()
            return
        
        if email == "Email" or not email:
            messagebox.showerror("Error", "Please enter your email")
            self.email_entry.focus()
            return
        
        if password == "Password" or not password:
            messagebox.showerror("Error", "Please enter your password")
            self.password_entry.focus()
            return
        
        try:
            # Create user object and attempt registration
            user = User(name=name, email=email, password=password)
            user_id = self.database.create_user(user)
            
            messagebox.showinfo("Success", "Registration successful! Please login.")
            self.on_register_success()
        
        except ValidationError as e:
            messagebox.showerror("Validation Error", str(e))
        except DatabaseError as e:
            messagebox.showerror("Database Error", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {e}") 