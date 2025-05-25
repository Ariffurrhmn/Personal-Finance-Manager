"""
Main application UI components
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable, Optional, List, Dict, Any
from datetime import datetime
try:
    from .config import COLORS, FONTS
    from .models import User, Account, Category, Transaction, ValidationError
    from .database import Database, DatabaseError
except ImportError:
    from config import COLORS, FONTS
    from models import User, Account, Category, Transaction, ValidationError
    from database import Database, DatabaseError

class PopupWindow:
    """Base class for popup windows"""
    
    def __init__(self, parent: tk.Tk, title: str, size: str = "340x250"):
        self.parent = parent
        self.popup = tk.Toplevel(parent)
        self.popup.geometry(size)
        self.popup.title(title)
        self.popup.configure(bg='#fdf3dd')
        self.popup.grab_set()  # Make popup modal
        
        # Center the popup
        self.popup.transient(parent)
        self.popup.focus()

class IncomePopup(PopupWindow):
    """Income entry popup"""
    
    def __init__(self, parent: tk.Tk, database: Database, user: User, 
                 accounts: List[Account], categories: List[Category],
                 on_success: Callable[[], None]):
        super().__init__(parent, "Add Income")
        self.database = database
        self.user = user
        self.accounts = accounts
        self.categories = [c for c in categories if c.category_type == "Income"]
        self.on_success = on_success
        
        self.amount_var = tk.StringVar()
        self.setup_ui()
    
    def setup_ui(self):
        """Setup income popup UI"""
        # Configure grid
        for i in range(4):
            self.popup.grid_rowconfigure(i, weight=1 if i in [0, 3] else 0)
        self.popup.grid_columnconfigure(0, weight=0)
        self.popup.grid_columnconfigure(1, weight=1)
        
        # Amount entry
        amount_entry = tk.Entry(self.popup, textvariable=self.amount_var, 
                               font=FONTS['POPUP_AMOUNT'], justify='left')
        amount_entry.grid(row=0, column=0, columnspan=2, sticky="nsew", ipady=0)
        amount_entry.focus()
        
        # Account dropdown
        account_label = tk.Label(self.popup, text="Account", anchor='w', 
                                font=FONTS['POPUP_LABEL'], bd=1, relief='solid')
        account_label.grid(row=1, column=0, sticky="nsew", ipadx=5, ipady=5)
        
        account_names = [f"{acc.name} ({acc.account_type})" for acc in self.accounts]
        self.account_combo = ttk.Combobox(self.popup, values=account_names, state="readonly")
        self.account_combo.grid(row=1, column=1, sticky="nsew", ipady=5)
        
        # Category dropdown
        category_label = tk.Label(self.popup, text="Category", anchor='w',
                                 font=FONTS['POPUP_LABEL'], bd=1, relief='solid')
        category_label.grid(row=2, column=0, sticky="nsew", ipadx=5, ipady=5)
        
        category_names = [cat.name for cat in self.categories]
        self.category_combo = ttk.Combobox(self.popup, values=category_names, state="readonly")
        self.category_combo.grid(row=2, column=1, sticky="nsew", ipady=5)
        
        # Description entry
        desc_label = tk.Label(self.popup, text="Description", anchor='w',
                             font=FONTS['FORM_LABEL'], bd=1, relief='solid')
        desc_label.grid(row=3, column=0, sticky="nsew", ipadx=5, ipady=5)
        
        self.desc_entry = tk.Entry(self.popup, bd=1, relief='solid')
        self.desc_entry.grid(row=3, column=1, sticky="nsew", ipady=5)
        
        # Submit button
        submit_btn = tk.Button(self.popup, text="SUBMIT", bg=COLORS['BLACK'], 
                              fg=COLORS['WHITE'], font=FONTS['POPUP_SUBMIT'], 
                              bd=0, command=self.submit)
        submit_btn.grid(row=4, column=0, columnspan=2, sticky="nsew", ipady=5)
        
        # Bind Enter key
        amount_entry.bind("<Return>", lambda e: self.submit())
        self.desc_entry.bind("<Return>", lambda e: self.submit())
    
    def submit(self):
        """Submit income transaction"""
        try:
            amount = float(self.amount_var.get())
            account_index = self.account_combo.current()
            category_index = self.category_combo.current()
            description = self.desc_entry.get().strip()
            
            if account_index == -1:
                messagebox.showerror("Error", "Please select an account")
                return
            
            if category_index == -1:
                messagebox.showerror("Error", "Please select a category")
                return
            
            account = self.accounts[account_index]
            category = self.categories[category_index]
            
            # Create transaction
            transaction = Transaction(
                user_id=self.user.user_id,
                account_id=account.account_id,
                category_id=category.category_id,
                amount=amount,
                description=description,
                transaction_type="Income"
            )
            
            self.database.create_transaction(transaction)
            self.popup.destroy()
            self.on_success()
            
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid amount")
        except ValidationError as e:
            messagebox.showerror("Validation Error", str(e))
        except DatabaseError as e:
            messagebox.showerror("Database Error", str(e))

class ExpensePopup(PopupWindow):
    """Expense entry popup"""
    
    def __init__(self, parent: tk.Tk, database: Database, user: User,
                 accounts: List[Account], categories: List[Category],
                 on_success: Callable[[], None]):
        super().__init__(parent, "Add Expense")
        self.database = database
        self.user = user
        self.accounts = accounts
        self.categories = [c for c in categories if c.category_type == "Expense"]
        self.on_success = on_success
        
        self.amount_var = tk.StringVar()
        self.setup_ui()
    
    def setup_ui(self):
        """Setup expense popup UI"""
        # Configure grid
        for i in range(5):
            self.popup.grid_rowconfigure(i, weight=1 if i in [0, 4] else 0)
        self.popup.grid_columnconfigure(0, weight=0)
        self.popup.grid_columnconfigure(1, weight=1)
        
        # Amount entry
        amount_entry = tk.Entry(self.popup, textvariable=self.amount_var,
                               font=FONTS['POPUP_AMOUNT'], justify='left')
        amount_entry.grid(row=0, column=0, columnspan=2, sticky="nsew", ipady=0)
        amount_entry.focus()
        
        # Account dropdown
        account_label = tk.Label(self.popup, text="Account", anchor='w',
                                font=FONTS['POPUP_LABEL'], bd=1, relief='solid')
        account_label.grid(row=1, column=0, sticky="nsew", ipadx=5, ipady=5)
        
        account_names = [f"{acc.name} ({acc.account_type})" for acc in self.accounts]
        self.account_combo = ttk.Combobox(self.popup, values=account_names, state="readonly")
        self.account_combo.grid(row=1, column=1, sticky="nsew", ipady=5)
        
        # Category dropdown
        category_label = tk.Label(self.popup, text="Category", anchor='w',
                                 font=FONTS['POPUP_LABEL'], bd=1, relief='solid')
        category_label.grid(row=2, column=0, sticky="nsew", ipadx=5, ipady=5)
        
        category_names = [cat.name for cat in self.categories]
        self.category_combo = ttk.Combobox(self.popup, values=category_names, state="readonly")
        self.category_combo.grid(row=2, column=1, sticky="nsew", ipady=5)
        
        # Description entry
        desc_label = tk.Label(self.popup, text="Description", anchor='w',
                             font=FONTS['FORM_LABEL'], bd=1, relief='solid')
        desc_label.grid(row=3, column=0, sticky="nsew", ipadx=5, ipady=5)
        
        self.desc_entry = tk.Entry(self.popup, bd=1, relief='solid')
        self.desc_entry.grid(row=3, column=1, sticky="nsew", ipady=5)
        
        # Submit button
        submit_btn = tk.Button(self.popup, text="SUBMIT", bg=COLORS['BLACK'],
                              fg=COLORS['WHITE'], font=FONTS['POPUP_SUBMIT'],
                              bd=0, command=self.submit)
        submit_btn.grid(row=4, column=0, columnspan=2, sticky="nsew", ipady=5)
        
        # Bind Enter key
        amount_entry.bind("<Return>", lambda e: self.submit())
        self.desc_entry.bind("<Return>", lambda e: self.submit())
    
    def submit(self):
        """Submit expense transaction"""
        try:
            amount = float(self.amount_var.get())
            account_index = self.account_combo.current()
            category_index = self.category_combo.current()
            description = self.desc_entry.get().strip()
            
            if account_index == -1:
                messagebox.showerror("Error", "Please select an account")
                return
            
            if category_index == -1:
                messagebox.showerror("Error", "Please select a category")
                return
            
            account = self.accounts[account_index]
            category = self.categories[category_index]
            
            # Create transaction
            transaction = Transaction(
                user_id=self.user.user_id,
                account_id=account.account_id,
                category_id=category.category_id,
                amount=amount,
                description=description,
                transaction_type="Expense"
            )
            
            self.database.create_transaction(transaction)
            self.popup.destroy()
            self.on_success()
            
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid amount")
        except ValidationError as e:
            messagebox.showerror("Validation Error", str(e))
        except DatabaseError as e:
            messagebox.showerror("Database Error", str(e))

class TransferPopup(PopupWindow):
    """Transfer popup"""
    
    def __init__(self, parent: tk.Tk, database: Database, user: User,
                 accounts: List[Account], on_success: Callable[[], None]):
        super().__init__(parent, "Transfer Balance", "350x240")
        self.database = database
        self.user = user
        self.accounts = accounts
        self.on_success = on_success
        
        self.amount_var = tk.StringVar()
        self.setup_ui()
    
    def setup_ui(self):
        """Setup transfer popup UI"""
        # Configure grid
        for i in range(5):
            self.popup.grid_rowconfigure(i, weight=0)
        self.popup.grid_columnconfigure(0, weight=0)
        self.popup.grid_columnconfigure(1, weight=1)
        
        # Amount entry
        amount_label = tk.Label(self.popup, text="Amount", anchor='w',
                               font=FONTS['BUTTON'], bd=1, relief='solid')
        amount_label.grid(row=0, column=0, sticky="nsew", ipadx=5, ipady=8)
        
        amount_entry = tk.Entry(self.popup, textvariable=self.amount_var,
                               font=('inter', 18, 'normal'), bd=1, relief='solid')
        amount_entry.grid(row=0, column=1, sticky="nsew", ipady=5)
        amount_entry.focus()
        
        # From account dropdown
        from_label = tk.Label(self.popup, text="From", anchor='w',
                             font=FONTS['POPUP_LABEL'], bd=1, relief='solid')
        from_label.grid(row=1, column=0, sticky="nsew", ipadx=5, ipady=8)
        
        account_names = [f"{acc.name} ({acc.account_type})" for acc in self.accounts]
        self.from_combo = ttk.Combobox(self.popup, values=account_names, state="readonly")
        self.from_combo.grid(row=1, column=1, sticky="nsew", ipady=5)
        
        # To account dropdown
        to_label = tk.Label(self.popup, text="To", anchor='w',
                           font=FONTS['POPUP_LABEL'], bd=1, relief='solid')
        to_label.grid(row=2, column=0, sticky="nsew", ipadx=5, ipady=8)
        
        self.to_combo = ttk.Combobox(self.popup, values=account_names, state="readonly")
        self.to_combo.grid(row=2, column=1, sticky="nsew", ipady=5)
        
        # Description entry
        desc_label = tk.Label(self.popup, text="Description", anchor='w',
                             font=FONTS['FORM_LABEL'], bd=1, relief='solid')
        desc_label.grid(row=3, column=0, sticky="nsew", ipadx=5, ipady=8)
        
        self.desc_entry = tk.Entry(self.popup, bd=1, relief='solid')
        self.desc_entry.grid(row=3, column=1, sticky="nsew", ipady=5)
        
        # Submit button
        submit_btn = tk.Button(self.popup, text="SUBMIT", bg=COLORS['BLACK'],
                              fg=COLORS['WHITE'], font=FONTS['POPUP_SUBMIT'],
                              bd=0, command=self.submit)
        submit_btn.grid(row=4, column=0, columnspan=2, sticky="nsew", ipady=5)
        
        # Bind Enter key
        amount_entry.bind("<Return>", lambda e: self.submit())
        self.desc_entry.bind("<Return>", lambda e: self.submit())
    
    def submit(self):
        """Submit transfer transaction"""
        try:
            amount = float(self.amount_var.get())
            from_index = self.from_combo.current()
            to_index = self.to_combo.current()
            description = self.desc_entry.get().strip()
            
            if from_index == -1:
                messagebox.showerror("Error", "Please select source account")
                return
            
            if to_index == -1:
                messagebox.showerror("Error", "Please select destination account")
                return
            
            if from_index == to_index:
                messagebox.showerror("Error", "Cannot transfer to the same account")
                return
            
            from_account = self.accounts[from_index]
            to_account = self.accounts[to_index]
            
            # Create transaction
            transaction = Transaction(
                user_id=self.user.user_id,
                account_id=from_account.account_id,
                amount=amount,
                description=description,
                transaction_type="Transfer",
                to_account_id=to_account.account_id
            )
            
            self.database.create_transaction(transaction)
            self.popup.destroy()
            self.on_success()
            
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid amount")
        except ValidationError as e:
            messagebox.showerror("Validation Error", str(e))
        except DatabaseError as e:
            messagebox.showerror("Database Error", str(e))

class MainApp:
    """Main application UI"""
    
    def __init__(self, parent: tk.Tk, database: Database, user: User, 
                 on_logout: Callable[[], None]):
        self.parent = parent
        self.database = database
        self.user = user
        self.on_logout = on_logout
        
        self.accounts = []
        self.categories = []
        self.selected_account_index = -1
        self.selected_category_index = -1
        
        self.setup_ui()
        self.refresh_data()
    
    def setup_ui(self):
        """Setup main application UI"""
        # Clear window
        for widget in self.parent.winfo_children():
            widget.destroy()
        
        # Welcome bar
        welcome_frame = tk.Frame(self.parent, bg=COLORS['BLACK'], height=40)
        welcome_frame.pack(fill='x')
        welcome_frame.pack_propagate(False)
        
        welcome_label = tk.Label(welcome_frame, text=f"Welcome, {self.user.name}!",
                                font=FONTS['WELCOME'], fg=COLORS['WHITE'], 
                                bg=COLORS['BLACK'])
        welcome_label.pack(side='left', padx=15, pady=10)
        
        logout_btn = tk.Button(welcome_frame, text="Logout", font=FONTS['LOGOUT'],
                              bg=COLORS['RED'], fg=COLORS['WHITE'], 
                              command=self.on_logout, relief='flat', bd=0, 
                              padx=15, pady=5)
        logout_btn.pack(side='right', padx=15, pady=8)
        
        # Create notebook (tabs)
        self.notebook = ttk.Notebook(self.parent)
        self.notebook.pack(fill='both', expand=True)
        
        # Create tab frames
        self.dash_frame = tk.Frame(self.notebook, bg=COLORS['FRAME_BG'])
        self.accounts_frame = tk.Frame(self.notebook, bg=COLORS['FRAME_BG'])
        self.categories_frame = tk.Frame(self.notebook, bg=COLORS['FRAME_BG'])
        
        self.notebook.add(self.dash_frame, text='Dashboard')
        self.notebook.add(self.accounts_frame, text='Edit Accounts')
        self.notebook.add(self.categories_frame, text='Edit Categories')
        
        self.setup_dashboard()
        self.setup_accounts_tab()
        self.setup_categories_tab()
    
    def setup_dashboard(self):
        """Setup dashboard tab"""
        # Configure grid
        self.dash_frame.grid_rowconfigure((0,1), weight=1, uniform="a")
        self.dash_frame.grid_columnconfigure(0, weight=1, uniform="a")
        
        # Top frame
        frame1 = tk.Frame(self.dash_frame, bg=COLORS['FRAME_BG'])
        frame1.grid(row=0, column=0, sticky="nsew", pady=(0,1))
        
        # Bottom frame (transactions)
        frame3 = tk.Frame(self.dash_frame, bg=COLORS['FRAME_BG'])
        frame3.grid(row=1, column=0, sticky="nsew", pady=(1,0))
        
        # Setup top frame layout
        frame1.grid_rowconfigure(0, weight=1, uniform='a')
        frame1.grid_rowconfigure((1,2), weight=1, uniform='a')
        frame1.grid_columnconfigure((0,1), weight=1, uniform='a')
        
        # Balance label
        self.balance_label = tk.Label(frame1, text="0.00 BDT", 
                                     font=FONTS['BALANCE'], 
                                     fg=COLORS['GREY'], bg=COLORS['FRAME_BG'])
        self.balance_label.grid(column=0, row=0, columnspan=2, sticky='nws')
        
        # Income section
        income_frame = tk.Frame(frame1, bg=COLORS['GREEN'], 
                               highlightbackground=COLORS['BLACK'], highlightthickness=5)
        income_frame.grid(row=1, column=0, sticky='nsew')
        income_frame.grid_rowconfigure((0,1,2), weight=1)
        income_frame.grid_columnconfigure(0, weight=1)
        
        tk.Label(income_frame, text="Income", font=FONTS['SECTION_LABEL'],
                fg=COLORS['BLACK'], bg=COLORS['GREEN']).grid(row=0, column=0, sticky='ne')
        
        self.income_label = tk.Label(income_frame, text="0.00 BDT", 
                                    font=FONTS['VALUE'], fg=COLORS['BLACK'], 
                                    bg=COLORS['GREEN'])
        self.income_label.grid(row=1, column=0, sticky='n')
        
        tk.Button(income_frame, text="Add Income", font=FONTS['BUTTON'],
                 fg=COLORS['BLACK'], bg=COLORS['GREEN'], relief='solid', 
                 borderwidth=1, command=self.open_income_popup).grid(row=2, column=0, sticky='n')
        
        # Expense section
        expense_frame = tk.Frame(frame1, bg=COLORS['GREY'],
                                highlightbackground=COLORS['BLACK'], highlightthickness=5)
        expense_frame.grid(row=1, column=1, sticky='nsew')
        expense_frame.grid_rowconfigure((0,1,2), weight=1)
        expense_frame.grid_columnconfigure(0, weight=1)
        
        tk.Label(expense_frame, text="Expense", font=FONTS['SECTION_LABEL'],
                fg=COLORS['BLACK'], bg=COLORS['GREY']).grid(row=0, column=0, sticky='ne')
        
        self.expense_label = tk.Label(expense_frame, text="0.00 BDT",
                                     font=FONTS['VALUE'], fg=COLORS['BLACK'],
                                     bg=COLORS['GREY'])
        self.expense_label.grid(row=1, column=0, sticky='n')
        
        tk.Button(expense_frame, text="Add Expense", font=FONTS['BUTTON'],
                 fg=COLORS['BLACK'], bg=COLORS['GREY'], relief='solid',
                 borderwidth=1, command=self.open_expense_popup).grid(row=2, column=0, sticky='n')
        
        # Cashflow section
        cashflow_frame = tk.Frame(frame1, bg=COLORS['GREY'],
                                 highlightbackground=COLORS['BLACK'], highlightthickness=5)
        cashflow_frame.grid(row=2, column=0, sticky='nsew')
        cashflow_frame.grid_rowconfigure((0,1), weight=1)
        cashflow_frame.grid_columnconfigure(0, weight=1)
        
        tk.Label(cashflow_frame, text="Cashflow", font=FONTS['SECTION_LABEL'],
                fg=COLORS['BLACK'], bg=COLORS['GREY']).grid(row=0, column=0, sticky='ne')
        
        self.cashflow_label = tk.Label(cashflow_frame, text="0.00 BDT",
                                      font=('inter', 18, 'bold'), fg=COLORS['BLACK'],
                                      bg=COLORS['GREY'])
        self.cashflow_label.grid(row=1, column=0, sticky='n')
        
        # Transfer button
        transfer_frame = tk.Frame(frame1, bg=COLORS['GREY'],
                                 highlightbackground=COLORS['BLACK'], highlightthickness=5)
        transfer_frame.grid(row=2, column=1, sticky='nsew')
        
        tk.Button(transfer_frame, text="Transfer Balance", font=('inter', 12, 'bold'),
                 fg=COLORS['BLACK'], bg=COLORS['GREEN'], relief='flat', borderwidth=0,
                 command=self.open_transfer_popup).pack(expand=True, fill='both', padx=(1,0))
        
        # Setup transaction list in frame3
        self.setup_transaction_list(frame3)
    
    def setup_transaction_list(self, parent_frame):
        """Setup scrollable transaction list"""
        parent_frame.grid_rowconfigure(0, weight=1)
        parent_frame.grid_columnconfigure(0, weight=1)
        
        # Container for canvas and scrollbar
        container = tk.Frame(parent_frame, bg=COLORS['FRAME_BG'])
        container.grid(row=0, column=0, sticky="nsew")
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        container.grid_columnconfigure(1, weight=0)
        
        # Canvas and scrollbar
        self.transaction_canvas = tk.Canvas(container, bg=COLORS['FRAME_BG'], highlightthickness=0)
        transaction_scrollbar = tk.Scrollbar(container, orient="vertical", 
                                           command=self.transaction_canvas.yview)
        
        self.transaction_canvas.grid(row=0, column=0, sticky='nsew')
        transaction_scrollbar.grid(row=0, column=1, sticky='ns')
        
        self.transaction_canvas.configure(yscrollcommand=transaction_scrollbar.set)
        
        # Frame for transaction items
        self.transaction_list_frame = tk.Frame(self.transaction_canvas, bg=COLORS['FRAME_BG'])
        self.transaction_window = self.transaction_canvas.create_window(
            (0, 0), window=self.transaction_list_frame, anchor="nw")
        
        self.transaction_list_frame.grid_columnconfigure(0, weight=1)
        
        # Bind scroll events
        self.transaction_list_frame.bind("<Configure>", self._on_transaction_configure)
        self.transaction_canvas.bind('<Configure>', self._on_canvas_configure)
        self.transaction_canvas.bind("<MouseWheel>", self._on_mousewheel)
    
    def _on_transaction_configure(self, event):
        """Update scroll region when transaction list changes"""
        self.transaction_canvas.configure(scrollregion=self.transaction_canvas.bbox("all"))
    
    def _on_canvas_configure(self, event):
        """Update transaction window width when canvas resizes"""
        canvas_width = event.width
        self.transaction_canvas.itemconfig(self.transaction_window, width=canvas_width)
    
    def _on_mousewheel(self, event):
        """Handle mouse wheel scrolling"""
        self.transaction_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    def setup_accounts_tab(self):
        """Setup accounts management tab"""
        self.accounts_frame.grid_rowconfigure(0, weight=0)  # Header
        self.accounts_frame.grid_rowconfigure(1, weight=1)  # List
        self.accounts_frame.grid_rowconfigure(2, weight=0)  # Form
        self.accounts_frame.grid_columnconfigure(0, weight=1)
        
        # Header
        tk.Label(self.accounts_frame, text="My Accounts", font=FONTS['HEADER'],
                fg=COLORS['GREY'], bg=COLORS['FRAME_BG']).grid(row=0, column=0, 
                pady=(30, 20), sticky='w', padx=30)
        
        # Accounts list with scrollbar
        self.setup_accounts_list()
        
        # Add account form
        self.setup_account_form()
    
    def setup_accounts_list(self):
        """Setup scrollable accounts list"""
        container = tk.Frame(self.accounts_frame, bg=COLORS['FRAME_BG'])
        container.grid(row=1, column=0, sticky='nsew', padx=30, pady=10)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        container.grid_columnconfigure(1, weight=0)
        
        self.accounts_canvas = tk.Canvas(container, bg=COLORS['FRAME_BG'], highlightthickness=0)
        accounts_scrollbar = tk.Scrollbar(container, orient="vertical", 
                                         command=self.accounts_canvas.yview)
        
        self.accounts_canvas.grid(row=0, column=0, sticky='nsew')
        accounts_scrollbar.grid(row=0, column=1, sticky='ns')
        
        self.accounts_canvas.configure(yscrollcommand=accounts_scrollbar.set)
        
        self.accounts_list_frame = tk.Frame(self.accounts_canvas, bg=COLORS['FRAME_BG'])
        self.accounts_window = self.accounts_canvas.create_window(
            (0, 0), window=self.accounts_list_frame, anchor="nw")
        
        self.accounts_list_frame.grid_columnconfigure(0, weight=1)
        
        # Bind events
        self.accounts_list_frame.bind("<Configure>", self._on_accounts_configure)
        self.accounts_canvas.bind('<Configure>', self._on_accounts_canvas_configure)
        self.accounts_canvas.bind("<MouseWheel>", self._on_accounts_mousewheel)
    
    def _on_accounts_configure(self, event):
        """Update accounts scroll region"""
        self.accounts_canvas.configure(scrollregion=self.accounts_canvas.bbox("all"))
    
    def _on_accounts_canvas_configure(self, event):
        """Update accounts window width"""
        canvas_width = event.width
        self.accounts_canvas.itemconfig(self.accounts_window, width=canvas_width)
    
    def _on_accounts_mousewheel(self, event):
        """Handle accounts mouse wheel scrolling"""
        self.accounts_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    def setup_account_form(self):
        """Setup add account form"""
        form_frame = tk.Frame(self.accounts_frame, bg=COLORS['FRAME_BG'])
        form_frame.grid(row=2, column=0, sticky='ew', padx=30, pady=30)
        form_frame.grid_columnconfigure(0, weight=1)
        
        tk.Label(form_frame, text="Add New Account", font=FONTS['FORM_HEADER'],
                fg=COLORS['GREY'], bg=COLORS['FRAME_BG']).grid(row=0, column=0, 
                sticky='w', pady=(0, 15))
        
        # Input fields
        input_frame = tk.Frame(form_frame, bg=COLORS['FRAME_BG'])
        input_frame.grid(row=1, column=0, sticky='ew')
        input_frame.grid_columnconfigure((0,1), weight=1)
        
        tk.Label(input_frame, text="Account Name:", font=FONTS['FORM_LABEL'],
                fg=COLORS['GREY'], bg=COLORS['FRAME_BG']).grid(row=0, column=0, sticky='w', pady=5)
        
        self.account_name_entry = tk.Entry(input_frame, font=FONTS['FORM_LABEL'], width=20)
        self.account_name_entry.grid(row=1, column=0, sticky='ew', padx=(0, 10))
        
        tk.Label(input_frame, text="Type:", font=FONTS['FORM_LABEL'],
                fg=COLORS['GREY'], bg=COLORS['FRAME_BG']).grid(row=0, column=1, sticky='w', pady=5)
        
        self.account_type_combo = ttk.Combobox(input_frame, values=Account.VALID_TYPES,
                                              font=FONTS['FORM_LABEL'], state="readonly")
        self.account_type_combo.grid(row=1, column=1, sticky='ew')
        
        # Buttons
        buttons_frame = tk.Frame(form_frame, bg=COLORS['FRAME_BG'])
        buttons_frame.grid(row=2, column=0, pady=20)
        
        tk.Button(buttons_frame, text="Add Account", font=FONTS['BUTTON'],
                 fg=COLORS['BLACK'], bg=COLORS['GREEN'], relief='flat', 
                 padx=20, pady=8, command=self.add_account).pack(side='left', padx=10)
        
        tk.Button(buttons_frame, text="Delete Selected", font=FONTS['BUTTON'],
                 fg=COLORS['WHITE'], bg=COLORS['RED'], relief='flat',
                 padx=20, pady=8, command=self.delete_account).pack(side='left', padx=10)
    
    def setup_categories_tab(self):
        """Setup categories management tab"""
        self.categories_frame.grid_rowconfigure(0, weight=0)  # Header
        self.categories_frame.grid_rowconfigure(1, weight=1)  # List
        self.categories_frame.grid_rowconfigure(2, weight=0)  # Form
        self.categories_frame.grid_columnconfigure(0, weight=1)
        
        # Header
        tk.Label(self.categories_frame, text="My Categories", font=FONTS['HEADER'],
                fg=COLORS['GREY'], bg=COLORS['FRAME_BG']).grid(row=0, column=0,
                pady=(30, 20), sticky='w', padx=30)
        
        # Categories list with scrollbar
        self.setup_categories_list()
        
        # Add category form
        self.setup_category_form()
    
    def setup_categories_list(self):
        """Setup scrollable categories list"""
        container = tk.Frame(self.categories_frame, bg=COLORS['FRAME_BG'])
        container.grid(row=1, column=0, sticky='nsew', padx=30, pady=10)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        container.grid_columnconfigure(1, weight=0)
        
        self.categories_canvas = tk.Canvas(container, bg=COLORS['FRAME_BG'], highlightthickness=0)
        categories_scrollbar = tk.Scrollbar(container, orient="vertical",
                                           command=self.categories_canvas.yview)
        
        self.categories_canvas.grid(row=0, column=0, sticky='nsew')
        categories_scrollbar.grid(row=0, column=1, sticky='ns')
        
        self.categories_canvas.configure(yscrollcommand=categories_scrollbar.set)
        
        self.categories_list_frame = tk.Frame(self.categories_canvas, bg=COLORS['FRAME_BG'])
        self.categories_window = self.categories_canvas.create_window(
            (0, 0), window=self.categories_list_frame, anchor="nw")
        
        self.categories_list_frame.grid_columnconfigure(0, weight=1)
        
        # Bind events
        self.categories_list_frame.bind("<Configure>", self._on_categories_configure)
        self.categories_canvas.bind('<Configure>', self._on_categories_canvas_configure)
        self.categories_canvas.bind("<MouseWheel>", self._on_categories_mousewheel)
    
    def _on_categories_configure(self, event):
        """Update categories scroll region"""
        self.categories_canvas.configure(scrollregion=self.categories_canvas.bbox("all"))
    
    def _on_categories_canvas_configure(self, event):
        """Update categories window width"""
        canvas_width = event.width
        self.categories_canvas.itemconfig(self.categories_window, width=canvas_width)
    
    def _on_categories_mousewheel(self, event):
        """Handle categories mouse wheel scrolling"""
        self.categories_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    def setup_category_form(self):
        """Setup add category form"""
        form_frame = tk.Frame(self.categories_frame, bg=COLORS['FRAME_BG'])
        form_frame.grid(row=2, column=0, sticky='ew', padx=30, pady=30)
        form_frame.grid_columnconfigure(0, weight=1)
        
        tk.Label(form_frame, text="Add New Category", font=FONTS['FORM_HEADER'],
                fg=COLORS['GREY'], bg=COLORS['FRAME_BG']).grid(row=0, column=0,
                sticky='w', pady=(0, 15))
        
        # Input fields
        input_frame = tk.Frame(form_frame, bg=COLORS['FRAME_BG'])
        input_frame.grid(row=1, column=0, sticky='ew')
        input_frame.grid_columnconfigure((0,1), weight=1)
        
        tk.Label(input_frame, text="Category Name:", font=FONTS['FORM_LABEL'],
                fg=COLORS['GREY'], bg=COLORS['FRAME_BG']).grid(row=0, column=0, sticky='w', pady=5)
        
        self.category_name_entry = tk.Entry(input_frame, font=FONTS['FORM_LABEL'], width=20)
        self.category_name_entry.grid(row=1, column=0, sticky='ew', padx=(0, 10))
        
        tk.Label(input_frame, text="Type:", font=FONTS['FORM_LABEL'],
                fg=COLORS['GREY'], bg=COLORS['FRAME_BG']).grid(row=0, column=1, sticky='w', pady=5)
        
        self.category_type_combo = ttk.Combobox(input_frame, values=Category.VALID_TYPES,
                                               font=FONTS['FORM_LABEL'], state="readonly")
        self.category_type_combo.grid(row=1, column=1, sticky='ew')
        
        # Buttons
        buttons_frame = tk.Frame(form_frame, bg=COLORS['FRAME_BG'])
        buttons_frame.grid(row=2, column=0, pady=20)
        
        tk.Button(buttons_frame, text="Add Category", font=FONTS['BUTTON'],
                 fg=COLORS['BLACK'], bg=COLORS['GREEN'], relief='flat',
                 padx=20, pady=8, command=self.add_category).pack(side='left', padx=10)
        
        tk.Button(buttons_frame, text="Delete Selected", font=FONTS['BUTTON'],
                 fg=COLORS['WHITE'], bg=COLORS['RED'], relief='flat',
                 padx=20, pady=8, command=self.delete_category).pack(side='left', padx=10)
    
    # Data management methods
    def refresh_data(self):
        """Refresh all data from database"""
        try:
            # Get fresh data
            self.accounts = self.database.get_user_accounts(self.user.user_id)
            self.categories = self.database.get_user_categories(self.user.user_id)
            summary = self.database.get_user_balance_summary(self.user.user_id)
            transactions = self.database.get_user_transactions(self.user.user_id)
            
            # Update dashboard
            self.balance_label.config(text=f"{summary['total_balance']:.2f} BDT")
            self.income_label.config(text=f"{summary['monthly_income']:.2f} BDT")
            self.expense_label.config(text=f"{summary['monthly_expense']:.2f} BDT")
            self.cashflow_label.config(text=f"{summary['monthly_cashflow']:.2f} BDT")
            
            # Update transaction list
            self.refresh_transaction_list(transactions)
            
            # Update account and category lists
            self.refresh_accounts_display()
            self.refresh_categories_display()
            
        except DatabaseError as e:
            messagebox.showerror("Database Error", str(e))
    
    def refresh_transaction_list(self, transactions: List[Dict[str, Any]]):
        """Refresh transaction list display"""
        # Clear existing transactions
        for widget in self.transaction_list_frame.winfo_children():
            widget.destroy()
        
        for i, trans in enumerate(transactions):
            # Determine background color
            if trans['transaction_type'] == 'Income':
                bg_color = COLORS['GREEN']
            else:
                bg_color = COLORS['GREY']
            
            # Create transaction item frame
            item_frame = tk.Frame(self.transaction_list_frame, bg=bg_color)
            item_frame.grid(row=i, column=0, sticky='nsew', pady=1)
            
            # Configure grid
            item_frame.grid_rowconfigure((0,1), weight=1)
            item_frame.grid_columnconfigure(0, weight=3)  # Description
            item_frame.grid_columnconfigure(1, weight=1)  # Amount
            item_frame.grid_columnconfigure(2, weight=1)  # Date
            
            # Description
            desc_text = trans['description'] or "No description"
            tk.Label(item_frame, text=desc_text, font=FONTS['TRANSACTION_DESC'],
                    fg=COLORS['BLACK'], bg=bg_color, anchor='w').grid(
                    row=0, column=0, sticky='nsew', padx=10, pady=(3,0))
            
            # Subtitle
            if trans['transaction_type'] == 'Transfer':
                subtitle = f"{trans['account_name']} → {trans['to_account_name']}"
            else:
                subtitle = f"{trans['account_name']} • {trans['category_name']}"
            
            tk.Label(item_frame, text=subtitle, font=FONTS['TRANSACTION_SUB'],
                    fg=COLORS['BLACK'], bg=bg_color, anchor='w').grid(
                    row=1, column=0, sticky='nsew', padx=10, pady=(0,3))
            
            # Amount
            prefix = "+" if trans['transaction_type'] == 'Income' else "-"
            amount_text = f"{prefix}{trans['amount']:.2f} BDT"
            tk.Label(item_frame, text=amount_text, font=FONTS['TRANSACTION_AMOUNT'],
                    fg=COLORS['BLACK'], bg=bg_color).grid(
                    row=0, rowspan=2, column=1, sticky='e', padx=10)
            
            # Date/Time
            try:
                dt = datetime.fromisoformat(trans['date_created'])
                date_str = dt.strftime("%Y-%m-%d")
                time_str = dt.strftime("%I:%M %p")
            except:
                date_str = trans['date_created'][:10]
                time_str = ""
            
            date_frame = tk.Frame(item_frame, bg=bg_color)
            date_frame.grid(row=0, column=2, sticky='ne', padx=10, pady=3)
            
            tk.Label(date_frame, text=date_str, font=FONTS['TRANSACTION_DATE'],
                    fg=COLORS['BLACK'], bg=bg_color).pack(anchor='e')
            
            if time_str:
                tk.Label(date_frame, text=time_str, font=FONTS['TRANSACTION_DATE'],
                        fg=COLORS['BLACK'], bg=bg_color).pack(anchor='e')
        
        # Update scroll region
        self.transaction_list_frame.update_idletasks()
        self.transaction_canvas.configure(scrollregion=self.transaction_canvas.bbox("all"))
    
    def refresh_accounts_display(self):
        """Refresh accounts list display"""
        # Clear existing items
        for widget in self.accounts_list_frame.winfo_children():
            widget.destroy()
        
        self.account_buttons = []
        
        for i, account in enumerate(self.accounts):
            btn = tk.Button(self.accounts_list_frame,
                           text=f"{account.name}\n{account.balance:.2f} BDT • {account.account_type}",
                           font=FONTS['LIST_ITEM'], bg=COLORS['GREY'], fg=COLORS['BLACK'],
                           relief='flat', pady=15, anchor='w', justify='left',
                           command=lambda idx=i: self.select_account(idx))
            btn.grid(row=i, column=0, sticky='ew', pady=5)
            self.account_buttons.append(btn)
        
        # Update scroll region
        self.accounts_list_frame.update_idletasks()
        self.accounts_canvas.configure(scrollregion=self.accounts_canvas.bbox("all"))
    
    def refresh_categories_display(self):
        """Refresh categories list display"""
        # Clear existing items
        for widget in self.categories_list_frame.winfo_children():
            widget.destroy()
        
        self.category_buttons = []
        
        for i, category in enumerate(self.categories):
            color = COLORS['LIGHT_GREEN'] if category.category_type == "Income" else COLORS['GREY']
            
            btn = tk.Button(self.categories_list_frame,
                           text=f"{category.name} ({category.category_type})",
                           font=FONTS['LIST_ITEM'], bg=color, fg=COLORS['BLACK'],
                           relief='flat', pady=12, anchor='w',
                           command=lambda idx=i: self.select_category(idx))
            btn.grid(row=i, column=0, sticky='ew', pady=3)
            self.category_buttons.append(btn)
        
        # Update scroll region
        self.categories_list_frame.update_idletasks()
        self.categories_canvas.configure(scrollregion=self.categories_canvas.bbox("all"))
    
    # Selection methods
    def select_account(self, index: int):
        """Select an account"""
        for i, btn in enumerate(self.account_buttons):
            if i == index:
                btn.configure(bg=COLORS['GREEN'])
                self.selected_account_index = index
            else:
                btn.configure(bg=COLORS['GREY'])
    
    def select_category(self, index: int):
        """Select a category"""
        for i, btn in enumerate(self.category_buttons):
            if i == index:
                btn.configure(bg=COLORS['GREEN'])
                self.selected_category_index = index
            else:
                category = self.categories[i]
                color = COLORS['LIGHT_GREEN'] if category.category_type == "Income" else COLORS['GREY']
                btn.configure(bg=color)
    
    # CRUD operations
    def add_account(self):
        """Add new account"""
        try:
            name = self.account_name_entry.get().strip()
            account_type = self.account_type_combo.get()
            
            if not name:
                messagebox.showerror("Error", "Account name is required")
                return
            
            if not account_type:
                messagebox.showerror("Error", "Account type is required")
                return
            
            account = Account(user_id=self.user.user_id, name=name, 
                            balance=0.0, account_type=account_type)
            
            self.database.create_account(account)
            self.account_name_entry.delete(0, tk.END)
            self.account_type_combo.set("")
            self.refresh_data()
            
        except ValidationError as e:
            messagebox.showerror("Validation Error", str(e))
        except DatabaseError as e:
            messagebox.showerror("Database Error", str(e))
    
    def delete_account(self):
        """Delete selected account"""
        if self.selected_account_index == -1:
            messagebox.showerror("Error", "Please select an account to delete")
            return
        
        account = self.accounts[self.selected_account_index]
        
        if messagebox.askyesno("Confirm Delete", 
                              f"Are you sure you want to delete '{account.name}'?"):
            try:
                self.database.delete_account(account.account_id, self.user.user_id)
                self.selected_account_index = -1
                self.refresh_data()
            except DatabaseError as e:
                messagebox.showerror("Database Error", str(e))
    
    def add_category(self):
        """Add new category"""
        try:
            name = self.category_name_entry.get().strip()
            category_type = self.category_type_combo.get()
            
            if not name:
                messagebox.showerror("Error", "Category name is required")
                return
            
            if not category_type:
                messagebox.showerror("Error", "Category type is required")
                return
            
            category = Category(user_id=self.user.user_id, name=name,
                              category_type=category_type)
            
            self.database.create_category(category)
            self.category_name_entry.delete(0, tk.END)
            self.category_type_combo.set("")
            self.refresh_data()
            
        except ValidationError as e:
            messagebox.showerror("Validation Error", str(e))
        except DatabaseError as e:
            messagebox.showerror("Database Error", str(e))
    
    def delete_category(self):
        """Delete selected category"""
        if self.selected_category_index == -1:
            messagebox.showerror("Error", "Please select a category to delete")
            return
        
        category = self.categories[self.selected_category_index]
        
        if messagebox.askyesno("Confirm Delete",
                              f"Are you sure you want to delete '{category.name}'?"):
            try:
                self.database.delete_category(category.category_id, self.user.user_id)
                self.selected_category_index = -1
                self.refresh_data()
            except DatabaseError as e:
                messagebox.showerror("Database Error", str(e))
    
    # Popup methods
    def open_income_popup(self):
        """Open income entry popup"""
        if not self.accounts:
            messagebox.showerror("Error", "Please add at least one account first")
            return
        
        income_categories = [c for c in self.categories if c.category_type == "Income"]
        if not income_categories:
            messagebox.showerror("Error", "Please add at least one income category first")
            return
        
        IncomePopup(self.parent, self.database, self.user, self.accounts, 
                   self.categories, self.refresh_data)
    
    def open_expense_popup(self):
        """Open expense entry popup"""
        if not self.accounts:
            messagebox.showerror("Error", "Please add at least one account first")
            return
        
        expense_categories = [c for c in self.categories if c.category_type == "Expense"]
        if not expense_categories:
            messagebox.showerror("Error", "Please add at least one expense category first")
            return
        
        ExpensePopup(self.parent, self.database, self.user, self.accounts,
                    self.categories, self.refresh_data)
    
    def open_transfer_popup(self):
        """Open transfer popup"""
        if len(self.accounts) < 2:
            messagebox.showerror("Error", "Please add at least two accounts to transfer between")
            return
        
        TransferPopup(self.parent, self.database, self.user, self.accounts, self.refresh_data) 