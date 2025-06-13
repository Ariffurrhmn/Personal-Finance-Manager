#!/usr/bin/env python3
import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import hashlib
import secrets
from contextlib import contextmanager
from datetime import datetime, timedelta

# Report generation imports (focus on preview only)
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
# =============================================================================
# CONFIGURATION
# =============================================================================
# Database configuration
DB_PATH = "finance_app.db"
DB_BACKUP_PATH = "finance_app_backup.db"
# UI Configuration
WINDOW_SIZE = "1024x768"
WINDOW_TITLE = "Finance Management"
# Color scheme
COLORS = {
    'FRAME_BG': "#000000",
    'GREY': "#D9D9D9", 
    'GREEN': "#0AFFB9",
    'LIGHT_GREEN': "#90EE90",
    'YELLOW': "#FFFF00",
    'BLACK': "#000000",
    'RED': "#FF0000",
    'BLUE': "#4A90E2",
    'WHITE': "#FFFFFF",
    'LIGHT_GREY': "#f0f0f0",
    'CYAN_GREEN': "#00FFBF",
    'DARK_GREY': "#D0D0D0"
}
# Font configuration with Arial fallback
FONT_FAMILY = ('inter', 'Arial')  # Try inter first, then Arial
FONTS = {
    'FAMILY': FONT_FAMILY,
    'BALANCE': (FONT_FAMILY, 36, 'bold'),
    'HEADER': (FONT_FAMILY, 22, 'bold'),
    'SECTION_LABEL': (FONT_FAMILY, 13, 'italic'),
    'VALUE': (FONT_FAMILY, 16, 'bold'),
    'BUTTON': (FONT_FAMILY, 11, 'bold'),
    'TRANSACTION_DESC': (FONT_FAMILY, 12, 'bold'),
    'TRANSACTION_SUB': (FONT_FAMILY, 10, 'italic'),
    'TRANSACTION_AMOUNT': (FONT_FAMILY, 14, 'bold'),
    'TRANSACTION_DATE': (FONT_FAMILY, 9, 'normal'),
    'POPUP_AMOUNT': (FONT_FAMILY, 50, 'normal'),
    'POPUP_LABEL': (FONT_FAMILY, 10, 'italic'),
    'POPUP_SUBMIT': (FONT_FAMILY, 22, 'bold'),
    'LOGIN_TITLE': (FONT_FAMILY, 32, 'bold'),
    'LOGIN_INPUT': (FONT_FAMILY, 14, 'normal'),
    'LOGIN_BUTTON': (FONT_FAMILY, 16, 'bold'),
    'WELCOME': (FONT_FAMILY, 12, 'normal'),
    'LOGOUT': (FONT_FAMILY, 10, 'bold'),
    'LIST_ITEM': (FONT_FAMILY, 13, 'normal'),
    'FORM_LABEL': (FONT_FAMILY, 11, 'normal'),
    'FORM_HEADER': (FONT_FAMILY, 16, 'bold')
}
# Security configuration
PASSWORD_MIN_LENGTH = 6
SALT_LENGTH = 16
# Default data
DEFAULT_ACCOUNTS = [
    {"name": "My Bank Account", "balance": 0.00, "type": "Bank"},
    {"name": "Cash Wallet", "balance": 0.00, "type": "Cash"},
]
DEFAULT_CATEGORIES = [
    {"name": "Food & Drink", "type": "Expense"},
    {"name": "Transport", "type": "Expense"},
    {"name": "Salary", "type": "Income"},
    {"name": "Education", "type": "Expense"},
    {"name": "Entertainment", "type": "Expense"},
]
# Account limits
ACCOUNT_LIMITS = {
    'MAX_ACCOUNTS_PER_USER': 5
}
# Validation rules
VALIDATION = {
    'MAX_AMOUNT': 999999999.99,
    'MIN_AMOUNT': 0.01,
    'MAX_NAME_LENGTH': 100,
    'MAX_DESC_LENGTH': 200
}
# Savings account specific rules
SAVINGS_CONFIG = {
    'MIN_BALANCE': 100.00,
    'MAX_MONTHLY_WITHDRAWALS': 6,
    'WITHDRAWAL_WARNING_THRESHOLD': 4
}
# Budget configuration
BUDGET_CONFIG = {
    'WARNING_THRESHOLD': 0.7,  # 70% threshold for red warning
    'TIME_PERIODS': ['Week', 'Month', 'Year']
}
# Default saving goal
DEFAULT_SAVING_GOAL = {
    'name': 'Saving is a good Habit',
    'target_amount': 0.0,
    'is_default': True
}
# =============================================================================
# MODELS
# =============================================================================
# Keep this for compatibility with existing code
class ValidationError(Exception):
    """Simple validation error"""
    pass
class DatabaseError(Exception):
    """Simple database error"""
    pass
# Simple validation helpers
def is_valid_name(name):
    """Check if name is valid"""
    if not name or len(name.strip()) == 0:
        return False
    if len(name) > 100:  # Simple limit
        return False
    return True
def is_valid_email(email):
    """Check if email looks valid"""
    if not email or "@" not in email or "." not in email:
        return False
    return True
def is_valid_amount(amount):
    """Check if amount is valid"""
    if amount < 0 or amount > 999999999:
        return False
    return True
def is_positive_amount(amount):
    """Check if amount is positive"""
    return amount > 0
class User:
    """Simple user class"""
    def __init__(self, user_id=None, name="", email="", password="", date_joined=None):
        self.user_id = user_id
        self.name = name
        self.email = email
        self.password = password
        self.date_joined = date_joined or datetime.now().isoformat()
    def is_valid(self):
        """Check if user data is valid"""
        if not is_valid_name(self.name):
            return False, "Name is required"
        if not is_valid_email(self.email):
            return False, "Invalid email"
        if not self.password or len(self.password) < 6:
            return False, "Password too short"
        return True, "OK"
class Account:
    """Simple account class"""
    def __init__(self, account_id=None, user_id=0, name="", balance=0.0, account_type="Bank"):
        self.account_id = account_id
        self.user_id = user_id
        self.name = name
        self.balance = balance
        self.account_type = account_type
    def is_valid(self):
        """Check if account data is valid"""
        if not is_valid_name(self.name):
            return False, "Account name required"
        if self.user_id <= 0:
            return False, "Invalid user"
        if not is_valid_amount(self.balance):
            return False, "Invalid balance"
        valid_types = ["Bank", "Cash", "Savings"]
        if self.account_type not in valid_types:
            return False, "Invalid account type"
        return True, "OK"
class Category:
    """Simple category class"""
    def __init__(self, category_id=None, user_id=0, name="", category_type="Expense"):
        self.category_id = category_id
        self.user_id = user_id
        self.name = name
        self.category_type = category_type
    def is_valid(self):
        """Check if category data is valid"""
        if not is_valid_name(self.name):
            return False, "Category name required"
        if self.user_id <= 0:
            return False, "Invalid user"
        valid_types = ["Income", "Expense"]
        if self.category_type not in valid_types:
            return False, "Invalid category type"
        return True, "OK"
class Transaction:
    """Simple transaction class"""
    def __init__(self, transaction_id=None, user_id=0, account_id=0, category_id=None,
                 amount=0.0, description="", transaction_type="Expense", 
                 to_account_id=None):
        self.transaction_id = transaction_id
        self.user_id = user_id
        self.account_id = account_id
        self.category_id = category_id
        self.amount = amount
        self.description = description
        self.transaction_type = transaction_type
        self.to_account_id = to_account_id
        self.date_created = datetime.now().isoformat()
    def is_valid(self):
        """Check if transaction data is valid"""
        # Amount must be positive
        if not is_positive_amount(self.amount):
            return False, "Amount must be positive"
        # Must have valid user
        if self.user_id <= 0:
            return False, "Invalid user"
        # Must have valid account
        if self.account_id <= 0:
            return False, "Invalid account"
        # Check transaction type
        valid_types = ["Income", "Expense", "Transfer"]
        if self.transaction_type not in valid_types:
            return False, "Invalid transaction type"
        # Income/Expense need category
        if self.transaction_type in ["Income", "Expense"] and not self.category_id:
            return False, "Category required"
        # Transfer needs destination account
        if self.transaction_type == "Transfer" and not self.to_account_id:
            return False, "Destination account required"
        # Can't transfer to same account
        if self.transaction_type == "Transfer" and self.account_id == self.to_account_id:
            return False, "Cannot transfer to same account"
        # Description length check
        if self.description and len(self.description) > 200:
            return False, "Description too long"
        return True, "OK" 
class SavingGoal:
    """Saving goal model with validation"""
    def __init__(self, goal_id, user_id=0, goal_name="", target_amount=0.0,
                 current_amount=0.0, account_id=None, is_default=False, date_created=None):
        self.goal_id = goal_id
        self.user_id = user_id
        self.goal_name = goal_name
        self.target_amount = target_amount
        self.current_amount = current_amount
        self.account_id = account_id
        self.is_default = is_default
        self.date_created = date_created or datetime.now().isoformat()
    def is_valid(self):
        """Check if saving goal data is valid"""
        if not is_valid_name(self.goal_name):
            return False, "Goal name required"
        if self.user_id <= 0:
            return False, "Invalid user"
        if not is_valid_amount(self.target_amount):
            return False, "Invalid target amount"
        if not is_valid_amount(self.current_amount):
            return False, "Invalid current amount"
        return True, "OK"
    def is_completed(self):
        """Check if goal is completed"""
        return self.current_amount >= self.target_amount and self.target_amount > 0
    def progress_percentage(self):
        """Get progress percentage"""
        if self.target_amount <= 0:
            return 0.0
        return min((self.current_amount / self.target_amount) * 100, 100.0)
class Budget:
    """Budget model with validation"""
    VALID_TIME_PERIODS = BUDGET_CONFIG['TIME_PERIODS']
    def __init__(self, budget_id=None, user_id=0, category_id=0, budget_amount=0.0,
                 time_period="Month", start_date=None, end_date=None, date_created=None):
        self.budget_id = budget_id
        self.user_id = user_id
        self.category_id = category_id
        self.budget_amount = budget_amount
        self.time_period = time_period
        self.start_date = start_date or datetime.now().isoformat()
        self.end_date = end_date or self._calculate_end_date()
        self.date_created = date_created or datetime.now().isoformat()
    def _calculate_end_date(self):
        """Calculate end date based on time period"""
        start = datetime.now()
        if self.time_period == "Week":
            end = start + timedelta(days=7)
        elif self.time_period == "Month":
            # Add one month
            if start.month == 12:
                end = start.replace(year=start.year + 1, month=1)
            else:
                end = start.replace(month=start.month + 1)
        elif self.time_period == "Year":
            end = start.replace(year=start.year + 1)
        else:
            end = start + timedelta(days=30)  # Default to 30 days
        return end.isoformat()
    def is_valid(self):
        """Check if budget data is valid"""
        if not is_positive_amount(self.budget_amount):
            return False, "Budget amount must be positive"
        if self.user_id <= 0:
            return False, "Invalid user"
        valid_periods = ['Week', 'Month', 'Year']
        if self.time_period not in valid_periods:
            return False, "Invalid time period"
        if self.category_id <= 0:
            return False, "Invalid category"
        return True, "OK"
    def is_expired(self):
        """Check if budget period has expired"""
        return datetime.now() > datetime.fromisoformat(self.end_date.replace('Z', '+00:00'))
    def days_remaining(self):
        """Get days remaining in budget period"""
        end_date = datetime.fromisoformat(self.end_date.replace('Z', '+00:00'))
        remaining = (end_date - datetime.now()).days
        return max(0, remaining)
# =============================================================================
# DATABASE LAYER
# =============================================================================
# Removed logging system for cleaner code
class Database:
    """Database management class with full CRUD operations"""
    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path
        self.init_database()
    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            yield conn
        except ValidationError:
            if conn:
                conn.rollback()
            raise
        except sqlite3.IntegrityError:
            if conn:
                conn.rollback()
            raise
        except sqlite3.Error as e:
            if conn:
                conn.rollback()
            raise DatabaseError(f"Database operation failed: {e}")
        finally:
            if conn:
                conn.close()
    def init_database(self):
        """Initialize database with all required tables"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            # Check if Account table exists and needs migration
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='Account'")
            account_table_exists = cursor.fetchone() is not None
            if account_table_exists:
                # Check current constraint by getting table schema
                cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='Account'")
                table_schema = cursor.fetchone()
                if table_schema and 'Internet Bank' in table_schema[0]:
                    # Need to migrate - old constraint detected
                    self._migrate_account_table(cursor)
            cursor.executescript("""
            CREATE TABLE IF NOT EXISTS User (
                UserID INTEGER PRIMARY KEY AUTOINCREMENT,
                Name TEXT NOT NULL,
                Email TEXT UNIQUE NOT NULL,
                Password TEXT NOT NULL,
                Salt TEXT NOT NULL,
                Date_Joined TEXT DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS Account (
                AccountID INTEGER PRIMARY KEY AUTOINCREMENT,
                UserID INTEGER NOT NULL,
                Name TEXT NOT NULL,
                Balance REAL NOT NULL DEFAULT 0.0,
                AccountType TEXT NOT NULL CHECK (AccountType IN ('Bank', 'Cash', 'Savings')),
                FOREIGN KEY (UserID) REFERENCES User(UserID) ON DELETE CASCADE
            );
            CREATE TABLE IF NOT EXISTS Category (
                CategoryID INTEGER PRIMARY KEY AUTOINCREMENT,
                UserID INTEGER NOT NULL,
                Name TEXT NOT NULL,
                CategoryType TEXT NOT NULL CHECK (CategoryType IN ('Income', 'Expense')),
                FOREIGN KEY (UserID) REFERENCES User(UserID) ON DELETE CASCADE
            );
            CREATE TABLE IF NOT EXISTS Transactions (
                TransactionID INTEGER PRIMARY KEY AUTOINCREMENT,
                UserID INTEGER NOT NULL,
                AccountID INTEGER NOT NULL,
                CategoryID INTEGER,
                Amount REAL NOT NULL CHECK (Amount > 0),
                Description TEXT,
                TransactionType TEXT NOT NULL CHECK (TransactionType IN ('Income', 'Expense', 'Transfer')),
                ToAccountID INTEGER,
                Date_Created TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (UserID) REFERENCES User(UserID) ON DELETE CASCADE,
                FOREIGN KEY (AccountID) REFERENCES Account(AccountID) ON DELETE CASCADE,
                FOREIGN KEY (CategoryID) REFERENCES Category(CategoryID) ON DELETE SET NULL,
                FOREIGN KEY (ToAccountID) REFERENCES Account(AccountID) ON DELETE CASCADE
            );
            CREATE INDEX IF NOT EXISTS idx_user_email ON User(Email);
            CREATE INDEX IF NOT EXISTS idx_account_user ON Account(UserID);
            CREATE INDEX IF NOT EXISTS idx_category_user ON Category(UserID);
            CREATE INDEX IF NOT EXISTS idx_transaction_user ON Transactions(UserID);
            CREATE INDEX IF NOT EXISTS idx_transaction_date ON Transactions(Date_Created);
            CREATE TABLE IF NOT EXISTS SavingGoal (
                GoalID INTEGER PRIMARY KEY AUTOINCREMENT,
                UserID INTEGER NOT NULL,
                GoalName TEXT NOT NULL,
                TargetAmount REAL NOT NULL DEFAULT 0.0,
                CurrentAmount REAL NOT NULL DEFAULT 0.0,
                AccountID INTEGER,
                IsDefault BOOLEAN NOT NULL DEFAULT 0,
                Date_Created TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (UserID) REFERENCES User(UserID) ON DELETE CASCADE,
                FOREIGN KEY (AccountID) REFERENCES Account(AccountID) ON DELETE CASCADE
            );
            CREATE TABLE IF NOT EXISTS Budget (
                BudgetID INTEGER PRIMARY KEY AUTOINCREMENT,
                UserID INTEGER NOT NULL,
                CategoryID INTEGER NOT NULL,
                BudgetAmount REAL NOT NULL CHECK (BudgetAmount > 0),
                TimePeriod TEXT NOT NULL CHECK (TimePeriod IN ('Week', 'Month', 'Year')),
                StartDate TEXT NOT NULL,
                EndDate TEXT NOT NULL,
                Date_Created TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (UserID) REFERENCES User(UserID) ON DELETE CASCADE,
                FOREIGN KEY (CategoryID) REFERENCES Category(CategoryID) ON DELETE CASCADE
            );
            CREATE INDEX IF NOT EXISTS idx_saving_goal_user ON SavingGoal(UserID);
            CREATE INDEX IF NOT EXISTS idx_budget_user ON Budget(UserID);
            CREATE INDEX IF NOT EXISTS idx_budget_category ON Budget(CategoryID);
            CREATE INDEX IF NOT EXISTS idx_budget_end_date ON Budget(EndDate);
            """)
            conn.commit()
    def _migrate_account_table(self, cursor):
        """Migrate Account table to support new account types"""
        # Create backup of existing data
        cursor.execute("""
            CREATE TEMPORARY TABLE Account_backup AS SELECT * FROM Account
        """)
        # Drop the old table
        cursor.execute("DROP TABLE Account")
        # Create new table with updated constraint
        cursor.execute("""
            CREATE TABLE Account (
                AccountID INTEGER PRIMARY KEY AUTOINCREMENT,
                UserID INTEGER NOT NULL,
                Name TEXT NOT NULL,
                Balance REAL NOT NULL DEFAULT 0.0,
                AccountType TEXT NOT NULL CHECK (AccountType IN ('Bank', 'Cash', 'Savings')),
                FOREIGN KEY (UserID) REFERENCES User(UserID) ON DELETE CASCADE
            )
        """)
        # Migrate data, converting 'Internet Bank' to 'Bank'
        cursor.execute("""
            INSERT INTO Account (AccountID, UserID, Name, Balance, AccountType)
            SELECT AccountID, UserID, Name, Balance, 
                   CASE WHEN AccountType = 'Internet Bank' THEN 'Bank' ELSE AccountType END
            FROM Account_backup
        """)
        # Drop the temporary table
        cursor.execute("DROP TABLE Account_backup")
        # Recreate the index
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_account_user ON Account(UserID)")
    def _hash_password(self, password, salt):
        """Hash password with salt"""
        return hashlib.sha256((password + salt).encode()).hexdigest()
    def _generate_salt(self):
        """Generate random salt"""
        return secrets.token_hex(SALT_LENGTH)
    def create_user(self, user):
        """Create a new user"""
        is_valid, error_msg = user.is_valid()
        if not is_valid:
            raise ValidationError(error_msg)
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                salt = self._generate_salt()
                hashed_password = self._hash_password(user.password, salt)
                cursor.execute("""
                    INSERT INTO User (Name, Email, Password, Salt, Date_Joined)
                    VALUES (?, ?, ?, ?, ?)
                """, (user.name, user.email, hashed_password, salt, user.date_joined))
                user_id = cursor.lastrowid
                # Create default accounts and categories for new user
                self._create_default_data(cursor, user_id)
                conn.commit()
            return user_id
        except sqlite3.IntegrityError as e:
            if "UNIQUE constraint failed: User.Email" in str(e):
                raise ValidationError("Email already exists")
            raise DatabaseError(f"Failed to create user: {e}")
        except DatabaseError:
            raise
    def _create_default_data(self, cursor, user_id):
        """Create default accounts and categories for new user"""
        # Create default accounts
        for acc_data in DEFAULT_ACCOUNTS:
            cursor.execute("""
                INSERT INTO Account (UserID, Name, Balance, AccountType)
                VALUES (?, ?, ?, ?)
            """, (user_id, acc_data["name"], acc_data["balance"], acc_data["type"]))
        # Create default categories
        for cat_data in DEFAULT_CATEGORIES:
            cursor.execute("""
                INSERT INTO Category (UserID, Name, CategoryType)
                VALUES (?, ?, ?)
            """, (user_id, cat_data["name"], cat_data["type"]))
        # Create default saving goal and account
        cursor.execute("""
            INSERT INTO Account (UserID, Name, Balance, AccountType)
            VALUES (?, ?, ?, ?)
        """, (user_id, f"{DEFAULT_SAVING_GOAL['name']} Fund", 0.0, "Savings"))
        saving_account_id = cursor.lastrowid
        cursor.execute("""
            INSERT INTO SavingGoal (UserID, GoalName, TargetAmount, CurrentAmount, AccountID, IsDefault)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (user_id, DEFAULT_SAVING_GOAL['name'], DEFAULT_SAVING_GOAL['target_amount'], 
              0.0, saving_account_id, DEFAULT_SAVING_GOAL['is_default']))
    def authenticate_user(self, email, password):
        """Authenticate user login"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM User WHERE Email = ?", (email,))
                row = cursor.fetchone()
                if row:
                    hashed_password = self._hash_password(password, row['Salt'])
                    if hashed_password == row['Password']:
                        return User(
                            user_id=row['UserID'],
                            name=row['Name'],
                            email=row['Email'],
                            password="",
                            date_joined=row['Date_Joined']
                        )
                return None
        except Exception as e:
            return None
    def get_user(self, user_id):
        """Get user by ID"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM User WHERE UserID = ?", (user_id,))
            row = cursor.fetchone()
            if row:
                return User(
                    user_id=row['UserID'],
                    name=row['Name'],
                    email=row['Email'],
                    password="",
                    date_joined=row['Date_Joined']
                )
            return None
    def create_account(self, account):
        """Create a new account"""
        is_valid, error_msg = account.is_valid()
        if not is_valid:
            raise ValidationError(error_msg)
        with self.get_connection() as conn:
            cursor = conn.cursor()
            # Check account limit
            cursor.execute("SELECT COUNT(*) as account_count FROM Account WHERE UserID = ?", 
                          (account.user_id,))
            account_count = cursor.fetchone()['account_count']
            if account_count >= ACCOUNT_LIMITS['MAX_ACCOUNTS_PER_USER']:
                raise ValidationError(f"Maximum {ACCOUNT_LIMITS['MAX_ACCOUNTS_PER_USER']} accounts allowed per user")
            cursor.execute("""
                INSERT INTO Account (UserID, Name, Balance, AccountType)
                VALUES (?, ?, ?, ?)
            """, (account.user_id, account.name, account.balance, account.account_type))
            account_id = cursor.lastrowid
            conn.commit()
            return account_id
    def get_user_accounts(self, user_id):
        """Get all accounts for a user"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Account WHERE UserID = ? ORDER BY AccountID", (user_id,))
            rows = cursor.fetchall()
            return [Account(
                account_id=row['AccountID'],
                user_id=row['UserID'],
                name=row['Name'],
                balance=row['Balance'],
                account_type=row['AccountType']
            ) for row in rows]
    def delete_account(self, account_id, user_id):
        """Delete an account"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM Account WHERE AccountID = ? AND UserID = ?", 
                          (account_id, user_id))
            success = cursor.rowcount > 0
            conn.commit()
            return success
    def create_category(self, category):
        """Create a new category"""
        is_valid, error_msg = category.is_valid()
        if not is_valid:
            raise ValidationError(error_msg)
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO Category (UserID, Name, CategoryType)
                VALUES (?, ?, ?)
            """, (category.user_id, category.name, category.category_type))
            category_id = cursor.lastrowid
            conn.commit()
            return category_id
    def get_user_categories(self, user_id):
        """Get all categories for a user"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Category WHERE UserID = ? ORDER BY CategoryType, Name", (user_id,))
            rows = cursor.fetchall()
            return [Category(
                category_id=row['CategoryID'],
                user_id=row['UserID'],
                name=row['Name'],
                category_type=row['CategoryType']
            ) for row in rows]
    def delete_category(self, category_id, user_id):
        """Delete a category"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM Category WHERE CategoryID = ? AND UserID = ?", 
                          (category_id, user_id))
            success = cursor.rowcount > 0
            conn.commit()
            return success
    def create_transaction(self, transaction):
        """Create a new transaction and update account balances"""
        is_valid, error_msg = transaction.is_valid()
        if not is_valid:
            raise ValidationError(error_msg)
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("BEGIN")
            try:
                # Check account balance for expenses and transfers
                if transaction.transaction_type in ["Expense", "Transfer"]:
                    cursor.execute("""
                        SELECT Balance, AccountType FROM Account 
                        WHERE AccountID = ?
                    """, (transaction.account_id,))
                    account_row = cursor.fetchone()
                    if not account_row:
                        raise ValidationError("Source account not found")
                    current_balance = account_row['Balance']
                    if transaction.amount > current_balance:
                        raise ValidationError(f"Insufficient balance. Available: {current_balance:.2f} BDT, Required: {transaction.amount:.2f} BDT")
                # Insert transaction
                cursor.execute("""
                    INSERT INTO Transactions (UserID, AccountID, CategoryID, Amount, Description, 
                                           TransactionType, ToAccountID, Date_Created)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (transaction.user_id, transaction.account_id, transaction.category_id,
                     transaction.amount, transaction.description, transaction.transaction_type,
                     transaction.to_account_id, transaction.date_created))
                transaction_id = cursor.lastrowid
                # Update account balances
                if transaction.transaction_type == "Income":
                    cursor.execute("UPDATE Account SET Balance = Balance + ? WHERE AccountID = ?",
                                 (transaction.amount, transaction.account_id))
                    # Update saving goal if this is a savings account
                    self._update_saving_goal_from_account(cursor, transaction.account_id)
                elif transaction.transaction_type == "Expense":
                    cursor.execute("UPDATE Account SET Balance = Balance - ? WHERE AccountID = ?",
                                 (transaction.amount, transaction.account_id))
                    # Update saving goal if this is a savings account
                    self._update_saving_goal_from_account(cursor, transaction.account_id)
                elif transaction.transaction_type == "Transfer":
                    cursor.execute("UPDATE Account SET Balance = Balance - ? WHERE AccountID = ?",
                                 (transaction.amount, transaction.account_id))
                    cursor.execute("UPDATE Account SET Balance = Balance + ? WHERE AccountID = ?",
                                 (transaction.amount, transaction.to_account_id))
                    # Update saving goals for both accounts if they are savings accounts
                    self._update_saving_goal_from_account(cursor, transaction.account_id)
                    self._update_saving_goal_from_account(cursor, transaction.to_account_id)
                conn.commit()
                return transaction_id
            except Exception as e:
                conn.rollback()
                raise DatabaseError(f"Failed to create transaction: {e}")
    def _update_saving_goal_from_account(self, cursor, account_id):
        """Update saving goal amount based on account balance"""
        # Check if this account is associated with a saving goal
        cursor.execute("""
            SELECT sg.GoalID, a.Balance, sg.CurrentAmount
            FROM SavingGoal sg 
            INNER JOIN Account a ON sg.AccountID = a.AccountID 
            WHERE a.AccountID = ?
        """, (account_id,))
        result = cursor.fetchone()
        if result:
            # Update the saving goal's current amount to match the account balance
            # This ensures they stay in sync
            cursor.execute("""
                UPDATE SavingGoal SET CurrentAmount = ? WHERE GoalID = ?
            """, (result['Balance'], result['GoalID']))
    def get_user_transactions(self, user_id, limit = 50):
        """Get transactions for a user with account and category info"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT t.*, a.Name as AccountName, c.Name as CategoryName,
                       ta.Name as ToAccountName
                FROM Transactions t
                LEFT JOIN Account a ON t.AccountID = a.AccountID
                LEFT JOIN Category c ON t.CategoryID = c.CategoryID
                LEFT JOIN Account ta ON t.ToAccountID = ta.AccountID
                WHERE t.UserID = ?
                ORDER BY t.Date_Created DESC
                LIMIT ?
            """, (user_id, limit))
            rows = cursor.fetchall()
            transactions = []
            for row in rows:
                transactions.append({
                    'transaction_id': row['TransactionID'],
                    'user_id': row['UserID'],
                    'account_id': row['AccountID'],
                    'account_name': row['AccountName'],
                    'category_id': row['CategoryID'],
                    'category_name': row['CategoryName'],
                    'amount': row['Amount'],
                    'description': row['Description'],
                    'transaction_type': row['TransactionType'],
                    'to_account_id': row['ToAccountID'],
                    'to_account_name': row['ToAccountName'],
                    'date_created': row['Date_Created']
                })
            return transactions
    def get_user_balance_summary(self, user_id):
        """Get balance summary for a user"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            # Total balance (excluding saving accounts)
            cursor.execute("""
                SELECT SUM(Balance) as TotalBalance 
                FROM Account 
                WHERE UserID = ? AND AccountType != 'Savings'
            """, (user_id,))
            total_balance = cursor.fetchone()['TotalBalance'] or 0.0
            # Total savings balance (separate from spending money)
            cursor.execute("""
                SELECT SUM(Balance) as TotalSavings 
                FROM Account 
                WHERE UserID = ? AND AccountType = 'Savings'
            """, (user_id,))
            total_savings = cursor.fetchone()['TotalSavings'] or 0.0
            # Income this month
            cursor.execute("""
                SELECT SUM(Amount) as MonthlyIncome FROM Transactions 
                WHERE UserID = ? AND TransactionType = 'Income' 
                AND date(Date_Created) >= date('now', 'start of month')
            """, (user_id,))
            monthly_income = cursor.fetchone()['MonthlyIncome'] or 0.0
            # Expenses this month
            cursor.execute("""
                SELECT SUM(Amount) as MonthlyExpense FROM Transactions 
                WHERE UserID = ? AND TransactionType = 'Expense' 
                AND date(Date_Created) >= date('now', 'start of month')
            """, (user_id,))
            monthly_expense = cursor.fetchone()['MonthlyExpense'] or 0.0
            return {
                'total_balance': total_balance,
                'total_savings': total_savings,
                'monthly_income': monthly_income,
                'monthly_expense': monthly_expense,
                'monthly_cashflow': monthly_income - monthly_expense
            }
    def close(self):
        """Close database connection"""
        pass 
    # =============================================================================
    # SAVING GOALS METHODS
    # =============================================================================
    def create_saving_goal(self, goal):
        """Create a new saving goal and associated saving account"""
        is_valid, error_msg = goal.is_valid()
        if not is_valid:
            raise ValidationError(error_msg)
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("BEGIN")
            try:
                # Create saving account
                account_name = f"{goal.goal_name} Fund"
                cursor.execute("""
                    INSERT INTO Account (UserID, Name, Balance, AccountType)
                    VALUES (?, ?, ?, ?)
                """, (goal.user_id, account_name, goal.current_amount, "Savings"))
                account_id = cursor.lastrowid
                # Create saving goal
                cursor.execute("""
                    INSERT INTO SavingGoal (UserID, GoalName, TargetAmount, CurrentAmount, AccountID, IsDefault, Date_Created)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (goal.user_id, goal.goal_name, goal.target_amount, goal.current_amount, 
                      account_id, goal.is_default, goal.date_created))
                goal_id = cursor.lastrowid
                conn.commit()
                return goal_id
            except Exception as e:
                conn.rollback()
                raise DatabaseError(f"Failed to create saving goal: {e}")
    def get_user_saving_goals(self, user_id):
        """Get all saving goals for a user"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM SavingGoal WHERE UserID = ? ORDER BY IsDefault DESC, Date_Created ASC
            """, (user_id,))
            rows = cursor.fetchall()
            return [SavingGoal(
                goal_id=row['GoalID'],
                user_id=row['UserID'],
                goal_name=row['GoalName'],
                target_amount=row['TargetAmount'],
                current_amount=row['CurrentAmount'],
                account_id=row['AccountID'],
                is_default=bool(row['IsDefault']),
                date_created=row['Date_Created']
            ) for row in rows]
    def update_saving_goal_amount(self, goal_id, new_amount):
        """Update saving goal current amount"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE SavingGoal SET CurrentAmount = ? WHERE GoalID = ?
            """, (new_amount, goal_id))
            success = cursor.rowcount > 0
            conn.commit()
            return success
    def delete_saving_goal(self, goal_id, user_id):
        """Delete saving goal and associated account"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("BEGIN")
            try:
                # Get account ID first
                cursor.execute("""
                    SELECT AccountID FROM SavingGoal WHERE GoalID = ? AND UserID = ?
                """, (goal_id, user_id))
                row = cursor.fetchone()
                if not row:
                    return False
                account_id = row['AccountID']
                # Delete saving goal first (due to foreign key)
                cursor.execute("""
                    DELETE FROM SavingGoal WHERE GoalID = ? AND UserID = ?
                """, (goal_id, user_id))
                # Delete associated account
                cursor.execute("""
                    DELETE FROM Account WHERE AccountID = ? AND UserID = ?
                """, (account_id, user_id))
                success = cursor.rowcount > 0
                conn.commit()
                return success
            except Exception as e:
                conn.rollback()
                raise DatabaseError(f"Failed to delete saving goal: {e}")
    def get_saving_accounts(self, user_id):
        """Get all saving accounts for a user"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT a.* FROM Account a
                INNER JOIN SavingGoal sg ON a.AccountID = sg.AccountID
                WHERE a.UserID = ?
                ORDER BY sg.IsDefault DESC, sg.Date_Created ASC
            """, (user_id,))
            rows = cursor.fetchall()
            return [Account(
                account_id=row['AccountID'],
                user_id=row['UserID'],
                name=row['Name'],
                balance=row['Balance'],
                account_type=row['AccountType']
            ) for row in rows]
    def get_regular_accounts(self, user_id):
        """Get non-saving accounts for a user"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT a.* FROM Account a
                LEFT JOIN SavingGoal sg ON a.AccountID = sg.AccountID
                WHERE a.UserID = ? AND sg.AccountID IS NULL
                ORDER BY a.AccountID
            """, (user_id,))
            rows = cursor.fetchall()
            return [Account(
                account_id=row['AccountID'],
                user_id=row['UserID'],
                name=row['Name'],
                balance=row['Balance'],
                account_type=row['AccountType']
            ) for row in rows]
    # =============================================================================
    # BUDGET METHODS
    # =============================================================================
    def create_budget(self, budget):
        """Create a new budget"""
        is_valid, error_msg = budget.is_valid()
        if not is_valid:
            raise ValidationError(error_msg)
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO Budget (UserID, CategoryID, BudgetAmount, TimePeriod, StartDate, EndDate, Date_Created)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (budget.user_id, budget.category_id, budget.budget_amount, budget.time_period,
                  budget.start_date, budget.end_date, budget.date_created))
            budget_id = cursor.lastrowid
            conn.commit()
            return budget_id
    def get_user_budgets_with_spending(self, user_id):
        """Get all active budgets for a user with spending calculations"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT b.*, c.Name as CategoryName,
                       COALESCE(SUM(CASE 
                           WHEN t.TransactionType = 'Expense' 
                           AND t.Date_Created >= b.StartDate 
                           AND t.Date_Created <= b.EndDate 
                           THEN t.Amount 
                           ELSE 0 
                       END), 0) as SpentAmount
                FROM Budget b
                LEFT JOIN Category c ON b.CategoryID = c.CategoryID
                LEFT JOIN Transactions t ON t.CategoryID = b.CategoryID AND t.UserID = b.UserID
                WHERE b.UserID = ? AND datetime(b.EndDate) > datetime('now')
                GROUP BY b.BudgetID, c.Name
                ORDER BY 
                    CASE WHEN (COALESCE(SUM(CASE 
                        WHEN t.TransactionType = 'Expense' 
                        AND t.Date_Created >= b.StartDate 
                        AND t.Date_Created <= b.EndDate 
                        THEN t.Amount 
                        ELSE 0 
                    END), 0) / b.BudgetAmount) >= 0.7 
                    THEN (COALESCE(SUM(CASE 
                        WHEN t.TransactionType = 'Expense' 
                        AND t.Date_Created >= b.StartDate 
                        AND t.Date_Created <= b.EndDate 
                        THEN t.Amount 
                        ELSE 0 
                    END), 0) / b.BudgetAmount) 
                    ELSE -1 
                    END DESC,
                    datetime(b.EndDate) ASC
            """, (user_id,))
            rows = cursor.fetchall()
            budgets = []
            for row in rows:
                spent_percentage = (row['SpentAmount'] / row['BudgetAmount']) if row['BudgetAmount'] > 0 else 0
                remaining = max(0, row['BudgetAmount'] - row['SpentAmount'])
                budgets.append({
                    'budget_id': row['BudgetID'],
                    'user_id': row['UserID'],
                    'category_id': row['CategoryID'],
                    'category_name': row['CategoryName'],
                    'budget_amount': row['BudgetAmount'],
                    'spent_amount': row['SpentAmount'],
                    'remaining_amount': remaining,
                    'spent_percentage': spent_percentage,
                    'time_period': row['TimePeriod'],
                    'start_date': row['StartDate'],
                    'end_date': row['EndDate'],
                    'is_over_threshold': spent_percentage >= BUDGET_CONFIG['WARNING_THRESHOLD'],
                    'days_remaining': max(0, (datetime.fromisoformat(row['EndDate']) - datetime.now()).days)
                })
            return budgets
    def delete_budget(self, budget_id, user_id):
        """Delete a budget"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM Budget WHERE BudgetID = ? AND UserID = ?", 
                          (budget_id, user_id))
            success = cursor.rowcount > 0
            conn.commit()
            return success
    def cleanup_expired_budgets(self, user_id):
        """Remove expired budgets and return count of removed budgets"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                DELETE FROM Budget WHERE UserID = ? AND datetime(EndDate) <= datetime('now')
            """, (user_id,))
            removed_count = cursor.rowcount
            conn.commit()
            return removed_count
    def check_budget_warning(self, user_id, category_id, amount):
        """Check if a transaction would exceed 75% of any budget and return warning info"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT b.*, c.Name as CategoryName,
                       COALESCE(SUM(t.Amount), 0) as CurrentSpent
                FROM Budget b
                LEFT JOIN Category c ON b.CategoryID = c.CategoryID
                LEFT JOIN Transactions t ON t.CategoryID = b.CategoryID 
                    AND t.UserID = b.UserID 
                    AND t.TransactionType = 'Expense'
                    AND t.Date_Created >= b.StartDate 
                    AND t.Date_Created <= b.EndDate
                WHERE b.UserID = ? AND b.CategoryID = ? 
                    AND datetime(b.EndDate) > datetime('now')
                GROUP BY b.BudgetID
            """, (user_id, category_id))
            row = cursor.fetchone()
            if not row:
                return None
            new_total = row['CurrentSpent'] + amount
            percentage_used = (new_total / row['BudgetAmount']) * 100
            if percentage_used >= 75.0:
                return {
                    'category_name': row['CategoryName'],
                    'budget_amount': row['BudgetAmount'],
                    'current_spent': row['CurrentSpent'],
                    'new_total': new_total,
                    'percentage_used': percentage_used,
                    'remaining': row['BudgetAmount'] - new_total
                }
            return None
    def check_budget_exceeded(self, user_id, category_id, amount):
        """Check if a transaction would exceed any budget"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT b.*, c.Name as CategoryName,
                       COALESCE(SUM(t.Amount), 0) as CurrentSpent
                FROM Budget b
                LEFT JOIN Category c ON b.CategoryID = c.CategoryID
                LEFT JOIN Transactions t ON t.CategoryID = b.CategoryID 
                    AND t.UserID = b.UserID 
                    AND t.TransactionType = 'Expense'
                    AND t.Date_Created >= b.StartDate 
                    AND t.Date_Created <= b.EndDate
                WHERE b.UserID = ? AND b.CategoryID = ? 
                    AND datetime(b.EndDate) > datetime('now')
                GROUP BY b.BudgetID
            """, (user_id, category_id))
            row = cursor.fetchone()
            if not row:
                return None
            new_total = row['CurrentSpent'] + amount
            if new_total > row['BudgetAmount']:
                return {
                    'category_name': row['CategoryName'],
                    'budget_amount': row['BudgetAmount'],
                    'current_spent': row['CurrentSpent'],
                    'new_total': new_total,
                    'exceeded_by': new_total - row['BudgetAmount']
                }
            return None
# =============================================================================
# UI COMPONENTS
# =============================================================================
class LoginScreen:
    """Login screen UI component"""
    def __init__(self, parent, database, 
                 on_login_success,
                 on_show_register):
        self.parent = parent
        self.database = database
        self.on_login_success = on_login_success
        self.on_show_register = on_show_register
        self.email_var = tk.StringVar()
        self.password_var = tk.StringVar()
        self.setup_ui()
    def setup_ui(self):
        """Setup the login screen UI for compact popup"""
        # Clear the window
        for widget in self.parent.winfo_children():
            widget.destroy()
        # Create main container
        main_frame = tk.Frame(self.parent, bg=COLORS['LIGHT_GREY'])
        main_frame.pack(fill='both', expand=True)
        # Black header section (smaller for popup)
        header_frame = tk.Frame(main_frame, bg=COLORS['BLACK'], height=80)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)
        # Title in header
        title_label = tk.Label(header_frame, text="Finance Manager", 
                              font=('inter', 20, 'bold'), 
                              fg=COLORS['WHITE'], 
                              bg=COLORS['BLACK'])
        title_label.pack(expand=True)
        # Body section
        body_frame = tk.Frame(main_frame, bg=COLORS['LIGHT_GREY'])
        body_frame.pack(fill='both', expand=True, padx=30, pady=20)
        # Email label and entry
        email_label = tk.Label(body_frame, text="Email", 
                              font=('inter', 12, 'bold'), 
                              fg=COLORS['BLACK'], bg=COLORS['LIGHT_GREY'])
        email_label.pack(anchor='w', pady=(0, 5))
        self.email_entry = tk.Entry(body_frame, textvariable=self.email_var, 
                                   font=('inter', 12, 'normal'), 
                                   relief='solid', bd=2, bg=COLORS['WHITE'])
        self.email_entry.pack(fill='x', pady=(0, 15), ipady=8)
        # Password label and entry
        password_label = tk.Label(body_frame, text="Password", 
                                 font=('inter', 12, 'bold'), 
                                 fg=COLORS['BLACK'], bg=COLORS['LIGHT_GREY'])
        password_label.pack(anchor='w', pady=(0, 5))
        self.password_entry = tk.Entry(body_frame, textvariable=self.password_var, 
                                      font=('inter', 12, 'normal'), 
                                      show="*", relief='solid', bd=2, bg=COLORS['WHITE'])
        self.password_entry.pack(fill='x', pady=(0, 20), ipady=8)
        # Bind Enter key to login
        self.email_entry.bind("<Return>", lambda e: self.login())
        self.password_entry.bind("<Return>", lambda e: self.login())
        # Login button
        login_btn = tk.Button(body_frame, text="Login", 
                             font=('inter', 14, 'bold'), 
                             bg=COLORS['CYAN_GREEN'], fg=COLORS['BLACK'], 
                             command=self.login, relief='flat', bd=0)
        login_btn.pack(fill='x', pady=(0, 10), ipady=12)
        # Register button
        register_btn = tk.Button(body_frame, text="Register", 
                                font=('inter', 14, 'bold'), 
                                bg=COLORS['DARK_GREY'], fg=COLORS['BLACK'], 
                                command=self.on_show_register, relief='flat', bd=0)
        register_btn.pack(fill='x', pady=(0, 10), ipady=12)
        # Set focus to email entry
        self.email_entry.focus()
    def login(self):
        """Handle login attempt"""
        email = self.email_var.get().strip()
        password = self.password_var.get().strip()
        # Validate input
        if not email:
            messagebox.showerror("Error", "Please enter your email")
            self.email_entry.focus()
            return
        if not password:
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
                self.email_entry.focus()
        except DatabaseError as e:
            messagebox.showerror("Database Error", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {e}")
class RegisterScreen:
    """Registration screen UI component"""
    def __init__(self, parent, database, 
                 on_register_success,
                 on_show_login):
        self.parent = parent
        self.database = database
        self.on_register_success = on_register_success
        self.on_show_login = on_show_login
        # Initialize string variables
        self.name_var = tk.StringVar()
        self.email_var = tk.StringVar()
        self.password_var = tk.StringVar()
        self.setup_ui()
    def setup_ui(self):
        """Setup the register screen UI for compact popup"""
        # Clear the window
        for widget in self.parent.winfo_children():
            widget.destroy()
        # Create main container
        main_frame = tk.Frame(self.parent, bg=COLORS['LIGHT_GREY'])
        main_frame.pack(fill='both', expand=True)
        # Black header section (smaller for popup)
        header_frame = tk.Frame(main_frame, bg=COLORS['BLACK'], height=80)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)
        # Title in header
        title_label = tk.Label(header_frame, text="Create Account", 
                              font=('inter', 18, 'bold'), 
                              fg=COLORS['WHITE'], 
                              bg=COLORS['BLACK'])
        title_label.pack(expand=True)
        # Body section
        body_frame = tk.Frame(main_frame, bg=COLORS['LIGHT_GREY'])
        body_frame.pack(fill='both', expand=True, padx=30, pady=15)
        # Name label and entry
        name_label = tk.Label(body_frame, text="Name", 
                             font=('inter', 11, 'bold'), 
                             fg=COLORS['BLACK'], bg=COLORS['LIGHT_GREY'])
        name_label.pack(anchor='w', pady=(0, 3))
        self.name_entry = tk.Entry(body_frame, textvariable=self.name_var, 
                                  font=('inter', 11, 'normal'), 
                                  relief='solid', bd=2, bg=COLORS['WHITE'])
        self.name_entry.pack(fill='x', pady=(0, 10), ipady=6)
        # Email label and entry
        email_label = tk.Label(body_frame, text="Email", 
                              font=('inter', 11, 'bold'), 
                              fg=COLORS['BLACK'], bg=COLORS['LIGHT_GREY'])
        email_label.pack(anchor='w', pady=(0, 3))
        self.email_entry = tk.Entry(body_frame, textvariable=self.email_var, 
                                   font=('inter', 11, 'normal'), 
                                   relief='solid', bd=2, bg=COLORS['WHITE'])
        self.email_entry.pack(fill='x', pady=(0, 10), ipady=6)
        # Password label and entry
        password_label = tk.Label(body_frame, text="Password", 
                                 font=('inter', 11, 'bold'), 
                                 fg=COLORS['BLACK'], bg=COLORS['LIGHT_GREY'])
        password_label.pack(anchor='w', pady=(0, 3))
        self.password_entry = tk.Entry(body_frame, textvariable=self.password_var, 
                                      font=('inter', 11, 'normal'), 
                                      show="*", relief='solid', bd=2, bg=COLORS['WHITE'])
        self.password_entry.pack(fill='x', pady=(0, 15), ipady=6)
        # Bind Enter key to register
        self.name_entry.bind("<Return>", lambda e: self.register())
        self.email_entry.bind("<Return>", lambda e: self.register())
        self.password_entry.bind("<Return>", lambda e: self.register())
        # Register button
        register_btn = tk.Button(body_frame, text="Create Account", 
                                font=('inter', 13, 'bold'), 
                                bg=COLORS['CYAN_GREEN'], fg=COLORS['BLACK'], 
                                command=self.register, relief='flat', bd=0)
        register_btn.pack(fill='x', pady=(0, 10), ipady=12)
        # Back to login button
        back_btn = tk.Button(body_frame, text="Back to Login", 
                            font=('inter', 13, 'bold'), 
                            bg=COLORS['DARK_GREY'], fg=COLORS['BLACK'], 
                            command=self.on_show_login, relief='flat', bd=0)
        back_btn.pack(fill='x', pady=(0, 10), ipady=12)
        # Set focus to name entry
        self.name_entry.focus()
    def register(self):
        """Handle registration attempt"""
        name = self.name_var.get().strip()
        email = self.email_var.get().strip()
        password = self.password_var.get().strip()
        # Validate input
        if not name:
            messagebox.showerror("Error", "Please enter your name")
            self.name_entry.focus()
            return
        if not email:
            messagebox.showerror("Error", "Please enter an email")
            self.email_entry.focus()
            return
        if not password:
            messagebox.showerror("Error", "Please enter a password")
            self.password_entry.focus()
            return
        try:
            # Create user object and attempt registration
            user = User(name=name, email=email, password=password)
            user_id = self.database.create_user(user)
            if user_id:
                messagebox.showinfo("Success", "Account created successfully! Please login.")
                self.on_show_login()
            else:
                messagebox.showerror("Error", "Registration failed. Email may already exist.")
        except Exception as e:
            logging.error(f"Registration error: {e}")
            messagebox.showerror("Error", "Registration failed. Please try again.")
class PopupWindow:
    """Base class for popup windows"""
    def __init__(self, parent, title, size = "340x250"):
        self.parent = parent
        self.popup = tk.Toplevel(parent)
        self.popup.geometry(size)
        self.popup.title(title)
        self.popup.configure(bg='#fdf3dd')
        self.popup.grab_set()
        self.popup.transient(parent)
        self.popup.focus()
class PaginationHelper:
    """Helper class for pagination logic"""
    def __init__(self, items_per_page = 10):
        self.items_per_page = items_per_page
        self.current_page = 0
    def get_page_items(self, all_items, page = None):
        """Get items for current page"""
        if page is not None:
            self.current_page = page
        start_idx = self.current_page * self.items_per_page
        end_idx = start_idx + self.items_per_page
        return all_items[start_idx:end_idx]
    def can_go_prev(self):
        """Check if can go to previous page"""
        return self.current_page > 0
    def can_go_next(self, total_items):
        """Check if can go to next page"""
        return (self.current_page + 1) * self.items_per_page < total_items
    def prev_page(self):
        """Go to previous page"""
        if self.can_go_prev():
            self.current_page -= 1
        return self.current_page
    def next_page(self, total_items):
        """Go to next page"""
        if self.can_go_next(total_items):
            self.current_page += 1
        return self.current_page
class TransactionPopup(PopupWindow):
    """Base class for transaction-related popups with common UI elements"""
    def __init__(self, parent, database, user, 
                 accounts, title, transaction_type,
                 on_success, categories = None):
        super().__init__(parent, title)
        self.database = database
        self.user = user
        self.accounts = accounts
        self.transaction_type = transaction_type
        self.on_success = on_success
        self.categories = categories or []
        self.amount_var = tk.StringVar()
        self.setup_common_ui()
    def setup_common_ui(self):
        """Setup common UI elements for transaction popups"""
        # Configure grid
        for i in range(5):
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
                                font=FONTS['POPUP_LABEL'], bg=COLORS['WHITE'])
        account_label.grid(row=1, column=0, sticky="nsew", ipadx=3, ipady=3)
        account_names = [f"{acc.name} ({acc.account_type})" for acc in self.accounts]
        self.account_combo = ttk.Combobox(self.popup, values=account_names, state="readonly")
        self.account_combo.grid(row=1, column=1, sticky="nsew", ipady=3)
        # Setup additional fields based on transaction type
        self.setup_specific_fields()
        # Submit button
        submit_btn = tk.Button(self.popup, text="SUBMIT", bg=COLORS['BLACK'], 
                              fg=COLORS['WHITE'], font=FONTS['POPUP_SUBMIT'], 
                              relief='flat', command=self.submit)
        submit_btn.grid(row=4, column=0, columnspan=2, sticky="nsew", ipady=3)
    def setup_specific_fields(self):
        """Override this method to setup specific fields for each transaction type"""
        pass
    def submit(self):
        """Submit transaction - override in subclasses"""
        pass
class IncomePopup(TransactionPopup):
    """Income entry popup"""
    def __init__(self, parent, database, user, 
                 accounts, categories,
                 on_success):
        income_categories = [c for c in categories if c.category_type == "Income"]
        super().__init__(parent, database, user, accounts, "Add Income", "Income", on_success, income_categories)
    def setup_specific_fields(self):
        """Setup income-specific fields"""
        # Category dropdown
        category_label = tk.Label(self.popup, text="Category", anchor='w',
                                 font=FONTS['POPUP_LABEL'], bg=COLORS['WHITE'])
        category_label.grid(row=2, column=0, sticky="nsew", ipadx=3, ipady=3)
        category_names = [cat.name for cat in self.categories]
        self.category_combo = ttk.Combobox(self.popup, values=category_names, state="readonly")
        self.category_combo.grid(row=2, column=1, sticky="nsew", ipady=3)
        # Description entry
        desc_label = tk.Label(self.popup, text="Description", anchor='w',
                             font=FONTS['FORM_LABEL'], bg=COLORS['WHITE'])
        desc_label.grid(row=3, column=0, sticky="nsew", ipadx=3, ipady=3)
        self.desc_entry = tk.Entry(self.popup)
        self.desc_entry.grid(row=3, column=1, sticky="nsew", ipady=3)
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
class ExpensePopup(TransactionPopup):
    """Expense entry popup"""
    def __init__(self, parent, database, user,
                 accounts, categories,
                 on_success):
        expense_categories = [c for c in categories if c.category_type == "Expense"]
        super().__init__(parent, database, user, accounts, "Add Expense", "Expense", on_success, expense_categories)
    def setup_specific_fields(self):
        """Setup expense-specific fields"""
        # Category dropdown
        category_label = tk.Label(self.popup, text="Category", anchor='w',
                                 font=FONTS['POPUP_LABEL'], bg=COLORS['WHITE'])
        category_label.grid(row=2, column=0, sticky="nsew", ipadx=3, ipady=3)
        category_names = [cat.name for cat in self.categories]
        self.category_combo = ttk.Combobox(self.popup, values=category_names, state="readonly")
        self.category_combo.grid(row=2, column=1, sticky="nsew", ipady=3)
        # Description entry
        desc_label = tk.Label(self.popup, text="Description", anchor='w',
                             font=FONTS['FORM_LABEL'], bg=COLORS['WHITE'])
        desc_label.grid(row=3, column=0, sticky="nsew", ipadx=3, ipady=3)
        self.desc_entry = tk.Entry(self.popup)
        self.desc_entry.grid(row=3, column=1, sticky="nsew", ipady=3)
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
            # Check for budget warnings (75% threshold)
            budget_warning = self.database.check_budget_warning(self.user.user_id, category.category_id, amount)
            if budget_warning:
                warning_message = (f"⚠️ Budget Warning for '{budget_warning['category_name']}'!\n\n"
                                 f"This expense will use {budget_warning['percentage_used']:.1f}% of your budget.\n"
                                 f"Budget: {budget_warning['budget_amount']:.2f} BDT\n"
                                 f"Already spent: {budget_warning['current_spent']:.2f} BDT\n"
                                 f"After this expense: {budget_warning['new_total']:.2f} BDT\n"
                                 f"Remaining: {budget_warning['remaining']:.2f} BDT\n\n"
                                 f"Do you want to proceed?")
                if not messagebox.askyesno("Budget Warning", warning_message):
                    return
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
    def __init__(self, parent, database, user,
                 accounts, on_success):
        super().__init__(parent, "Transfer Balance", "350x220")
        self.database = database
        self.user = user
        self.accounts = accounts
        self.on_success = on_success
        self.amount_var = tk.StringVar()
        self.setup_ui()
    def setup_ui(self):
        """Setup transfer popup UI"""
        for i in range(4):
            self.popup.grid_rowconfigure(i, weight=0)
        self.popup.grid_columnconfigure(0, weight=0)
        self.popup.grid_columnconfigure(1, weight=1)
        # Amount row
        amount_label = tk.Label(self.popup, text="Amount", anchor='w', 
                               font=FONTS['BUTTON'], bg=COLORS['WHITE'])
        amount_label.grid(row=0, column=0, sticky="nsew", ipadx=3, ipady=4)
        amount_entry = tk.Entry(self.popup, textvariable=self.amount_var, 
                               font=('inter', 18, 'normal'), bg=COLORS['WHITE'])
        amount_entry.grid(row=0, column=1, sticky="nsew", ipady=3)
        # From Account row
        from_label = tk.Label(self.popup, text="From", anchor='w', 
                             font=FONTS['POPUP_LABEL'], bg=COLORS['WHITE'])
        from_label.grid(row=1, column=0, sticky="nsew", ipadx=3, ipady=4)
        account_names = [f"{acc.name} ({acc.account_type})" for acc in self.accounts]
        self.from_combo = ttk.Combobox(self.popup, values=account_names, state="readonly")
        self.from_combo.grid(row=1, column=1, sticky="nsew", ipady=3)
        # To Account row
        to_label = tk.Label(self.popup, text="To", anchor='w', 
                           font=FONTS['POPUP_LABEL'], bg=COLORS['WHITE'])
        to_label.grid(row=2, column=0, sticky="nsew", ipadx=3, ipady=4)
        self.to_combo = ttk.Combobox(self.popup, values=account_names, state="readonly")
        self.to_combo.grid(row=2, column=1, sticky="nsew", ipady=3)
        # Description row
        desc_label = tk.Label(self.popup, text="Description", anchor='w', 
                             font=FONTS['FORM_LABEL'], bg=COLORS['WHITE'])
        desc_label.grid(row=3, column=0, sticky="nsew", ipadx=3, ipady=4)
        self.desc_entry = tk.Entry(self.popup)
        self.desc_entry.grid(row=3, column=1, sticky="nsew", ipady=3)
        # Submit button
        submit_btn = tk.Button(self.popup, text="SUBMIT", bg=COLORS['BLACK'], 
                              fg=COLORS['WHITE'], font=FONTS['POPUP_SUBMIT'], 
                              relief='flat', command=self.submit)
        submit_btn.grid(row=4, column=0, columnspan=2, sticky="nsew", ipady=3)
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
            # Create transfer transaction
            transaction = Transaction(
                user_id=self.user.user_id,
                account_id=from_account.account_id,
                category_id=None,
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
class SavingGoalPopup(PopupWindow):
    """Saving goal creation popup"""
    def __init__(self, parent, database, user, on_success):
        super().__init__(parent, "Add Saving Goal", "400x250")
        self.database = database
        self.user = user
        self.on_success = on_success
        self.goal_name_var = tk.StringVar()
        self.target_amount_var = tk.StringVar()
        self.current_saving_var = tk.StringVar(value="0")
        self.setup_ui()
    def setup_ui(self):
        """Setup saving goal popup UI matching the mockup"""
        # Configure grid to match mockup layout
        for i in range(4):
            self.popup.grid_rowconfigure(i, weight=1)
        self.popup.grid_columnconfigure(0, weight=1)
        self.popup.grid_columnconfigure(1, weight=2)
        # Goal Name row
        goal_name_label = tk.Label(self.popup, text="Goal Name", anchor='w', 
                                  font=FONTS['FORM_LABEL'], bg=COLORS['WHITE'])
        goal_name_label.grid(row=0, column=0, sticky="nsew", ipadx=5, ipady=8)
        goal_name_entry = tk.Entry(self.popup, textvariable=self.goal_name_var, 
                                  font=FONTS['FORM_LABEL'], bg=COLORS['WHITE'])
        goal_name_entry.grid(row=0, column=1, sticky="nsew", ipady=8)
        goal_name_entry.focus()
        # Target Amount row
        target_amount_label = tk.Label(self.popup, text="Target Amount", anchor='w', 
                                      font=FONTS['FORM_LABEL'], bg=COLORS['WHITE'])
        target_amount_label.grid(row=1, column=0, sticky="nsew", ipadx=5, ipady=8)
        target_amount_entry = tk.Entry(self.popup, textvariable=self.target_amount_var, 
                                      font=FONTS['FORM_LABEL'], bg=COLORS['WHITE'])
        target_amount_entry.grid(row=1, column=1, sticky="nsew", ipady=8)
        # Current Saving row
        current_saving_label = tk.Label(self.popup, text="Current Saving", anchor='w', 
                                       font=FONTS['FORM_LABEL'], bg=COLORS['WHITE'])
        current_saving_label.grid(row=2, column=0, sticky="nsew", ipadx=5, ipady=8)
        current_saving_entry = tk.Entry(self.popup, textvariable=self.current_saving_var, 
                                       font=FONTS['FORM_LABEL'], bg=COLORS['WHITE'])
        current_saving_entry.grid(row=2, column=1, sticky="nsew", ipady=8)
        # Submit button
        submit_btn = tk.Button(self.popup, text="SUBMIT", bg=COLORS['BLACK'], 
                              fg=COLORS['WHITE'], font=FONTS['POPUP_SUBMIT'], 
                              relief='flat', command=self.submit)
        submit_btn.grid(row=3, column=0, columnspan=2, sticky="nsew", ipady=8)
    def submit(self):
        """Submit saving goal creation"""
        try:
            goal_name = self.goal_name_var.get().strip()
            target_amount_str = self.target_amount_var.get().strip()
            current_amount_str = self.current_saving_var.get().strip()
            if not goal_name:
                messagebox.showerror("Error", "Please enter a goal name")
                return
            # Validate target amount
            try:
                target_amount = float(target_amount_str) if target_amount_str else 0.0
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid target amount")
                return
            # Validate current amount
            try:
                current_amount = float(current_amount_str) if current_amount_str else 0.0
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid current saving amount")
                return
            # Additional validation
            if target_amount < 0:
                messagebox.showerror("Error", "Target amount cannot be negative")
                return
            if current_amount < 0:
                messagebox.showerror("Error", "Current saving amount cannot be negative")
                return
            if target_amount > 0 and current_amount > target_amount:
                if not messagebox.askyesno("Warning", 
                    f"Current saving ({current_amount:.2f}) is greater than target ({target_amount:.2f}). Continue?"):
                    return
            # Create saving goal
            goal = SavingGoal(
                user_id=self.user.user_id,
                goal_name=goal_name,
                target_amount=target_amount,
                current_amount=current_amount
            )
            self.database.create_saving_goal(goal)
            messagebox.showinfo("Success", f"Saving goal '{goal_name}' created successfully!")
            self.popup.destroy()
            self.on_success()
        except ValidationError as e:
            messagebox.showerror("Validation Error", str(e))
        except DatabaseError as e:
            messagebox.showerror("Database Error", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create saving goal: {e}")
class BudgetPopup(PopupWindow):
    """Budget creation popup"""
    def __init__(self, parent, database, user, 
                 categories, on_success):
        super().__init__(parent, "Add Budget", "400x250")
        self.database = database
        self.user = user
        self.categories = [c for c in categories if c.category_type == "Expense"]
        self.on_success = on_success
        self.budget_amount_var = tk.StringVar()
        self.setup_ui()
    def setup_ui(self):
        """Setup budget popup UI matching the mockup"""
        # Configure grid to match mockup layout
        for i in range(4):
            self.popup.grid_rowconfigure(i, weight=1)
        self.popup.grid_columnconfigure(0, weight=1)
        self.popup.grid_columnconfigure(1, weight=2)
        # Category row
        category_label = tk.Label(self.popup, text="Category", anchor='w', 
                                 font=FONTS['FORM_LABEL'], bg=COLORS['WHITE'])
        category_label.grid(row=0, column=0, sticky="nsew", ipadx=5, ipady=8)
        category_names = [cat.name for cat in self.categories]
        self.category_combo = ttk.Combobox(self.popup, values=category_names, state="readonly")
        self.category_combo.grid(row=0, column=1, sticky="nsew", ipady=8)
        # Budget Amount row
        budget_amount_label = tk.Label(self.popup, text="Budget Amount", anchor='w', 
                                      font=FONTS['FORM_LABEL'], bg=COLORS['WHITE'])
        budget_amount_label.grid(row=1, column=0, sticky="nsew", ipadx=5, ipady=8)
        budget_amount_entry = tk.Entry(self.popup, textvariable=self.budget_amount_var, 
                                      font=FONTS['FORM_LABEL'], bg=COLORS['WHITE'])
        budget_amount_entry.grid(row=1, column=1, sticky="nsew", ipady=8)
        budget_amount_entry.focus()
        # Time row
        time_label = tk.Label(self.popup, text="Time", anchor='w', 
                             font=FONTS['FORM_LABEL'], bg=COLORS['WHITE'])
        time_label.grid(row=2, column=0, sticky="nsew", ipadx=5, ipady=8)
        self.time_combo = ttk.Combobox(self.popup, values=BUDGET_CONFIG['TIME_PERIODS'], state="readonly")
        self.time_combo.set("Month")  # Default to Month
        self.time_combo.grid(row=2, column=1, sticky="nsew", ipady=8)
        # Submit button
        submit_btn = tk.Button(self.popup, text="SUBMIT", bg=COLORS['BLACK'], 
                              fg=COLORS['WHITE'], font=FONTS['POPUP_SUBMIT'], 
                              relief='flat', command=self.submit)
        submit_btn.grid(row=3, column=0, columnspan=2, sticky="nsew", ipady=8)
    def submit(self):
        """Submit budget creation"""
        try:
            category_index = self.category_combo.current()
            budget_amount = float(self.budget_amount_var.get())
            time_period = self.time_combo.get()
            if category_index == -1:
                messagebox.showerror("Error", "Please select a category")
                return
            if not time_period:
                messagebox.showerror("Error", "Please select a time period")
                return
            category = self.categories[category_index]
            # Create budget
            budget = Budget(
                user_id=self.user.user_id,
                category_id=category.category_id,
                budget_amount=budget_amount,
                time_period=time_period
            )
            self.database.create_budget(budget)
            self.popup.destroy()
            self.on_success()
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid budget amount")
        except ValidationError as e:
            messagebox.showerror("Validation Error", str(e))
        except DatabaseError as e:
            messagebox.showerror("Database Error", str(e))
# =============================================================================
# MAIN APPLICATION UI
# =============================================================================
class MainApp:
    """Main application UI"""
    def __init__(self, parent, database, user, 
                 on_logout):
        self.parent = parent
        self.database = database
        self.user = user
        self.on_logout = on_logout
        # Data
        self.accounts = []
        self.categories = []
        self.saving_goals = []
        self.budgets = []
        self.selected_account_index = -1
        self.selected_category_index = -1
        self.selected_saving_goal_index = -1
        self.selected_budget_index = -1
        self.setup_ui()
        self.refresh_data()
    def setup_ui(self):
        """Setup the main application UI"""
        # Clear the window
        for widget in self.parent.winfo_children():
            widget.destroy()
        # Welcome header
        welcome_frame = tk.Frame(self.parent, bg=COLORS['BLACK'], height=40)
        welcome_frame.pack(fill='x')
        welcome_frame.pack_propagate(False)
        welcome_label = tk.Label(welcome_frame, text=f"Welcome, {self.user.name}!", 
                                font=FONTS['WELCOME'], fg=COLORS['WHITE'], bg=COLORS['BLACK'])
        welcome_label.pack(side='left', padx=15, pady=10)
        logout_btn = tk.Button(welcome_frame, text="Logout", font=FONTS['LOGOUT'], 
                              bg=COLORS['RED'], fg=COLORS['WHITE'], command=self.on_logout, 
                              relief='flat', bd=0, padx=15, pady=5)
        logout_btn.pack(side='right', padx=15, pady=8)
        # Create Notebook (tabs)
        self.notebook = ttk.Notebook(self.parent)
        self.notebook.pack(fill='both', expand=True)
        # Setup tabs
        self.setup_dashboard()
        self.setup_accounts_tab()
        self.setup_categories_tab()
        self.setup_saving_goals_tab()
        self.setup_budgets_tab()
        self.setup_reports_tab()
    def setup_dashboard(self):
        """Setup dashboard tab with 4 quadrants"""
        dash_frame = tk.Frame(self.notebook)
        self.notebook.add(dash_frame, text='Dashboard')
        # Configure main grid - 2 rows, 2 columns, all equal weight
        dash_frame.grid_rowconfigure((0,1), weight=1, uniform="row")
        dash_frame.grid_columnconfigure((0,1), weight=1, uniform="col")
        # Top Left quadrant - balance and actions
        frame_top_left = tk.Frame(dash_frame, bg=COLORS['FRAME_BG'], relief='flat', bd=1)
        frame_top_left.grid(row=0, column=0, sticky="nsew", padx=(2,1), pady=(2,1))
        # Bottom Left quadrant - transactions with pagination
        frame_bottom_left = tk.Frame(dash_frame, bg=COLORS['FRAME_BG'], relief='flat', bd=1)
        frame_bottom_left.grid(row=1, column=0, sticky="nsew", padx=(2,1), pady=(1,2))
        # Top Right quadrant - saving goals (changed to black)
        frame_top_right = tk.Frame(dash_frame, bg=COLORS['FRAME_BG'], relief='flat', bd=1)
        frame_top_right.grid(row=0, column=1, sticky="nsew", padx=(1,2), pady=(2,1))
        # Bottom Right quadrant - budget tracker (changed to black)
        frame_bottom_right = tk.Frame(dash_frame, bg=COLORS['FRAME_BG'], relief='flat', bd=1)
        frame_bottom_right.grid(row=1, column=1, sticky="nsew", padx=(1,2), pady=(1,2))
        # Setup Top Left quadrant content (existing balance/income/expense section)
        self.setup_balance_section(frame_top_left)
        # Setup Bottom Left quadrant content (existing transactions)
        self.setup_transaction_list_with_pagination(frame_bottom_left)
        # Setup Right quadrant content
        self.setup_saving_goals_tracker(frame_top_right)
        self.setup_budget_tracker(frame_bottom_right)
    def setup_balance_section(self, parent_frame):
        """Setup the balance and action buttons section"""
        # Setup grid for balance and buttons
        parent_frame.grid_rowconfigure(0, weight=1, uniform='a')
        parent_frame.grid_rowconfigure((1,2), weight=1, uniform='a')
        parent_frame.grid_columnconfigure((0,1), weight=1, uniform='a')
        # Balance display
        self.balance_label = tk.Label(parent_frame, text="0.00 BDT", font=FONTS['BALANCE'], 
                                     fg=COLORS['GREY'], bg=COLORS['FRAME_BG'])
        self.balance_label.grid(column=0, row=0, columnspan=2, sticky='nws', padx=10, pady=8)
        # Income section
        income_frame = tk.Frame(parent_frame, bg=COLORS['GREEN'], relief='solid', bd=1)
        income_frame.grid(row=1, column=0, sticky='nsew', padx=5, pady=5)
        income_frame.grid_rowconfigure((0,1,2), weight=1, uniform='a')
        income_frame.grid_columnconfigure(0, weight=1)
        income_label = tk.Label(income_frame, text="Income", font=FONTS['SECTION_LABEL'], 
                               fg=COLORS['BLACK'], bg=COLORS['GREEN'])
        income_label.grid(row=0, column=0, sticky='ne', padx=8, pady=4)
        self.income_value_label = tk.Label(income_frame, text="0.00 BDT", font=FONTS['VALUE'], 
                                          fg=COLORS['BLACK'], bg=COLORS['GREEN'])
        self.income_value_label.grid(row=1, column=0, sticky='n', padx=8, pady=2)
        add_income_btn = tk.Button(income_frame, text="Add Income", font=FONTS['BUTTON'], 
                                  fg=COLORS['BLACK'], bg=COLORS['GREEN'], relief='flat', bd=0,
                                  command=self.open_income_popup)
        add_income_btn.grid(row=2, column=0, sticky='ew', padx=8, pady=6)
        # Expense section
        expense_frame = tk.Frame(parent_frame, bg=COLORS['GREY'], relief='solid', bd=1)
        expense_frame.grid(row=1, column=1, sticky='nsew', padx=5, pady=5)
        expense_frame.grid_rowconfigure((0,1,2), weight=1, uniform='a')
        expense_frame.grid_columnconfigure(0, weight=1)
        expense_label = tk.Label(expense_frame, text="Expense", font=FONTS['SECTION_LABEL'], 
                                fg=COLORS['BLACK'], bg=COLORS['GREY'])
        expense_label.grid(row=0, column=0, sticky='ne', padx=8, pady=4)
        self.expense_value_label = tk.Label(expense_frame, text="0.00 BDT", font=FONTS['VALUE'], 
                                           fg=COLORS['BLACK'], bg=COLORS['GREY'])
        self.expense_value_label.grid(row=1, column=0, sticky='n', padx=8, pady=2)
        add_expense_btn = tk.Button(expense_frame, text="Add Expense", font=FONTS['BUTTON'], 
                                   fg=COLORS['BLACK'], bg=COLORS['GREY'], relief='flat', bd=0,
                                   command=self.open_expense_popup)
        add_expense_btn.grid(row=2, column=0, sticky='ew', padx=8, pady=6)
        # Cashflow section (bottom left)
        cashflow_frame = tk.Frame(parent_frame, bg=COLORS['GREY'], relief='flat', bd=2)
        cashflow_frame.grid(row=2, column=0, sticky='nsew', padx=5, pady=5)
        cashflow_frame.grid_rowconfigure((0,1), weight=1, uniform='a')
        cashflow_frame.grid_columnconfigure(0, weight=1)
        cashflow_label = tk.Label(cashflow_frame, text="Cashflow", font=FONTS['SECTION_LABEL'], 
                                 fg=COLORS['BLACK'], bg=COLORS['GREY'])
        cashflow_label.grid(row=0, column=0, sticky='ne', padx=8, pady=4)
        self.cashflow_label = tk.Label(cashflow_frame, text="0.00 BDT", font=('inter', 18, 'bold'), 
                                      fg=COLORS['BLACK'], bg=COLORS['GREY'])
        self.cashflow_label.grid(row=1, column=0, sticky='n', padx=8, pady=4)
        # Transfer button (bottom right)
        transfer_frame = tk.Frame(parent_frame, bg=COLORS['GREY'], relief='flat', bd=0)
        transfer_frame.grid(row=2, column=1, sticky='nsew', padx=5, pady=5)
        transfer_btn = tk.Button(transfer_frame, text="Transfer Balance", 
                                font=FONTS['TRANSACTION_DESC'], fg=COLORS['BLACK'], 
                                bg=COLORS['GREEN'], relief='flat', bd=0,
                                command=self.open_transfer_popup)
        transfer_btn.pack(expand=True, fill='both', padx=0, pady=0)
    def setup_placeholder_frame(self, parent_frame, text):
        """Setup a placeholder frame with centered text"""
        label = tk.Label(parent_frame, text=text, font=FONTS['HEADER'], 
                        fg=COLORS['BLACK'], bg=COLORS['WHITE'])
        label.pack(expand=True)
    def setup_transaction_list_with_pagination(self, parent_frame):
        """Setup transaction list with pagination"""
        # Setup pagination for transactions
        parent_frame.grid_rowconfigure(0, weight=1)  # Transaction list
        parent_frame.grid_rowconfigure(1, weight=0)  # Pagination controls
        parent_frame.grid_columnconfigure(0, weight=1)
        # Transaction list frame (no canvas/scrollbar)
        self.transaction_list = tk.Frame(parent_frame, bg=COLORS['FRAME_BG'], relief='flat', bd=1)
        self.transaction_list.grid(row=0, column=0, sticky="nsew", padx=8, pady=8)
        self.transaction_list.grid_columnconfigure(0, weight=1)
        # Pagination variables
        self.current_page = 0
        self.items_per_page = 4
        self.total_pages = 1
        # Pagination controls
        pagination_frame = tk.Frame(parent_frame, bg=COLORS['FRAME_BG'], relief='flat', bd=1)
        pagination_frame.grid(row=1, column=0, sticky="ew", padx=8, pady=(0,8))
        pagination_frame.grid_columnconfigure(1, weight=1)
        self.prev_btn = tk.Button(pagination_frame, text="Previous", font=('inter', 10, 'normal'), 
                                 bg=COLORS['GREY'], fg=COLORS['BLACK'], command=self.prev_page, 
                                 relief='flat', bd=1, padx=15, pady=5)
        self.prev_btn.grid(row=0, column=0, padx=8, pady=5)
        self.page_label = tk.Label(pagination_frame, text="Page 1 of 1", 
                                  font=('inter', 10, 'normal'), fg=COLORS['GREY'], bg=COLORS['FRAME_BG'])
        self.page_label.grid(row=0, column=1, pady=5)
        self.next_btn = tk.Button(pagination_frame, text="Next", font=('inter', 10, 'normal'), 
                                 bg=COLORS['GREY'], fg=COLORS['BLACK'], command=self.next_page, 
                                 relief='flat', bd=1, padx=15, pady=5)
        self.next_btn.grid(row=0, column=2, padx=8, pady=5)
    def display_transactions(self):
        """Display transactions for current page"""
        # Clear existing transactions
        for widget in self.transaction_list.winfo_children():
            widget.destroy()
        # Get transactions from database
        all_transactions = self.database.get_user_transactions(self.user.user_id, limit=50)
        # Calculate pagination
        self.total_pages = max(1, (len(all_transactions) + self.items_per_page - 1) // self.items_per_page)
        start_idx = self.current_page * self.items_per_page
        end_idx = min(start_idx + self.items_per_page, len(all_transactions))
        page_transactions = all_transactions[start_idx:end_idx]
        # Display transactions using 2-column layout from ToBreak
        for i, transaction in enumerate(page_transactions):
            frame_bg = COLORS['GREEN'] if transaction["transaction_type"] == "Income" else COLORS['GREY']
            transaction_item = tk.Frame(self.transaction_list, bg=frame_bg, relief='flat', bd=1)
            transaction_item.grid(row=i, column=0, sticky='nsew', pady=2, padx=4)
            transaction_item.grid_columnconfigure(0, weight=1)
            transaction_item.grid_columnconfigure(1, weight=0)
            # Left side - Description and details
            left_text = f"{transaction['description'] or 'No description'}\n{transaction['account_name']} • {transaction['category_name'] or 'Transfer'}"
            desc_label = tk.Label(transaction_item, 
                                 text=left_text,
                                 font=('inter', 11, 'normal'),
                                 fg=COLORS['BLACK'],
                                 bg=frame_bg,
                                 anchor='w',
                                 justify='left')
            desc_label.grid(row=0, column=0, sticky='nsew', padx=8, pady=6)
            # Right side - Amount and date
            prefix = "+" if transaction["transaction_type"] == "Income" else "-"
            if transaction["transaction_type"] == "Transfer":
                prefix = "→"
            # Format date for display
            try:
                date_obj = datetime.fromisoformat(transaction['date_created'].replace('Z', '+00:00'))
                formatted_date = date_obj.strftime("%d/%m/%Y")
            except:
                formatted_date = transaction['date_created'][:10]
            right_text = f"{prefix}{transaction['amount']:.2f} BDT\n{formatted_date}"
            amount_label = tk.Label(transaction_item, 
                                  text=right_text,
                                  font=('inter', 11, 'bold'),
                                  fg=COLORS['BLACK'],
                                  bg=frame_bg,
                                  anchor='e',
                                  justify='right')
            amount_label.grid(row=0, column=1, sticky='nsew', padx=8, pady=6)
        # Update pagination buttons
        self.prev_btn.config(state="normal" if self.current_page > 0 else "disabled")
        self.next_btn.config(state="normal" if self.current_page < self.total_pages - 1 else "disabled")
        self.page_label.config(text=f"Page {self.current_page + 1} of {self.total_pages}")
    def prev_page(self):
        """Go to previous page"""
        if self.current_page > 0:
            self.current_page -= 1
            self.display_transactions()
    def next_page(self):
        """Go to next page"""
        if self.current_page < self.total_pages - 1:
            self.current_page += 1
            self.display_transactions()
    def setup_accounts_tab(self):
        """Setup accounts management tab"""
        accounts_frame = tk.Frame(self.notebook, bg=COLORS['FRAME_BG'])
        self.notebook.add(accounts_frame, text='Accounts')
        accounts_frame.grid_rowconfigure(1, weight=1)
        accounts_frame.grid_columnconfigure(0, weight=1)
        # Header
        header_label = tk.Label(accounts_frame, text="My Accounts", font=FONTS['HEADER'], 
                               fg=COLORS['GREY'], bg=COLORS['FRAME_BG'])
        header_label.grid(row=0, column=0, pady=15, sticky='w', padx=20)
        # Accounts list
        self.accounts_list_frame = tk.Frame(accounts_frame, bg=COLORS['FRAME_BG'], relief='flat', bd=2)
        self.accounts_list_frame.grid(row=1, column=0, sticky='nsew', padx=20, pady=10)
        self.accounts_list_frame.grid_columnconfigure(0, weight=1)
        # Add account form
        form_frame = tk.Frame(accounts_frame, bg=COLORS['FRAME_BG'], relief='flat', bd=2)
        form_frame.grid(row=2, column=0, sticky='ew', padx=20, pady=15)
        form_frame.grid_columnconfigure((0,1,2), weight=1)
        tk.Label(form_frame, text="Account Name:", font=FONTS['FORM_LABEL'], 
                fg=COLORS['GREY'], bg=COLORS['FRAME_BG']).grid(row=0, column=0, sticky='w', pady=4, padx=8)
        self.account_name_var = tk.StringVar()
        tk.Entry(form_frame, textvariable=self.account_name_var, font=FONTS['FORM_LABEL'],
                bg=COLORS['WHITE'], fg=COLORS['BLACK'], relief='flat', bd=1).grid(row=1, column=0, sticky='ew', padx=(8,5), ipady=4)
        tk.Label(form_frame, text="Type:", font=FONTS['FORM_LABEL'], 
                fg=COLORS['GREY'], bg=COLORS['FRAME_BG']).grid(row=0, column=1, sticky='w', pady=4, padx=8)
        self.account_type_combo = ttk.Combobox(form_frame, values=["Bank", "Cash", "Savings"], state="readonly")
        self.account_type_combo.grid(row=1, column=1, sticky='ew', padx=(8,5), ipady=4)
        add_account_btn = tk.Button(form_frame, text="Add Account", font=FONTS['BUTTON'], 
                                   bg=COLORS['GREEN'], fg=COLORS['BLACK'], command=self.add_account,
                                   relief='flat', bd=2, padx=15, pady=6)
        add_account_btn.grid(row=1, column=2, sticky='ew', padx=8)
        delete_account_btn = tk.Button(form_frame, text="Delete Selected", font=FONTS['BUTTON'], 
                                      bg=COLORS['RED'], fg=COLORS['WHITE'], command=self.delete_account,
                                      relief='flat', bd=2, padx=15, pady=6)
        delete_account_btn.grid(row=2, column=2, sticky='ew', padx=8, pady=(6,8))
    def setup_categories_tab(self):
        """Setup categories management tab"""
        categories_frame = tk.Frame(self.notebook, bg=COLORS['FRAME_BG'])
        self.notebook.add(categories_frame, text='Categories')
        categories_frame.grid_rowconfigure(1, weight=1)
        categories_frame.grid_columnconfigure(0, weight=1)
        # Header
        header_label = tk.Label(categories_frame, text="My Categories", font=FONTS['HEADER'], 
                               fg=COLORS['GREY'], bg=COLORS['FRAME_BG'])
        header_label.grid(row=0, column=0, pady=15, sticky='w', padx=20)
        # Categories list
        self.categories_list_frame = tk.Frame(categories_frame, bg=COLORS['FRAME_BG'], relief='flat', bd=2)
        self.categories_list_frame.grid(row=1, column=0, sticky='nsew', padx=20, pady=10)
        self.categories_list_frame.grid_columnconfigure(0, weight=1)
        # Add category form
        form_frame = tk.Frame(categories_frame, bg=COLORS['FRAME_BG'], relief='flat', bd=2)
        form_frame.grid(row=2, column=0, sticky='ew', padx=20, pady=15)
        form_frame.grid_columnconfigure((0,1,2), weight=1)
        tk.Label(form_frame, text="Category Name:", font=FONTS['FORM_LABEL'], 
                fg=COLORS['GREY'], bg=COLORS['FRAME_BG']).grid(row=0, column=0, sticky='w', pady=4, padx=8)
        self.category_name_var = tk.StringVar()
        tk.Entry(form_frame, textvariable=self.category_name_var, font=FONTS['FORM_LABEL'],
                bg=COLORS['WHITE'], fg=COLORS['BLACK'], relief='flat', bd=1).grid(row=1, column=0, sticky='ew', padx=(8,5), ipady=4)
        tk.Label(form_frame, text="Type:", font=FONTS['FORM_LABEL'], 
                fg=COLORS['GREY'], bg=COLORS['FRAME_BG']).grid(row=0, column=1, sticky='w', pady=4, padx=8)
        self.category_type_combo = ttk.Combobox(form_frame, values=["Income", "Expense"], state="readonly")
        self.category_type_combo.grid(row=1, column=1, sticky='ew', padx=(8,5), ipady=4)
        add_category_btn = tk.Button(form_frame, text="Add Category", font=FONTS['BUTTON'], 
                                    bg=COLORS['GREEN'], fg=COLORS['BLACK'], command=self.add_category,
                                    relief='flat', bd=2, padx=15, pady=6)
        add_category_btn.grid(row=1, column=2, sticky='ew', padx=8)
        delete_category_btn = tk.Button(form_frame, text="Delete Selected", font=FONTS['BUTTON'], 
                                       bg=COLORS['RED'], fg=COLORS['WHITE'], command=self.delete_category,
                                       relief='flat', bd=2, padx=15, pady=6)
        delete_category_btn.grid(row=2, column=2, sticky='ew', padx=8, pady=(6,8))
    def setup_saving_goals_tab(self):
        """Setup saving goals management tab"""
        saving_goals_frame = tk.Frame(self.notebook, bg=COLORS['FRAME_BG'])
        self.notebook.add(saving_goals_frame, text='Saving Goals')
        saving_goals_frame.grid_rowconfigure(1, weight=1)
        saving_goals_frame.grid_columnconfigure(0, weight=1)
        # Header
        header_label = tk.Label(saving_goals_frame, text="Saving Goals", font=FONTS['HEADER'], 
                               fg=COLORS['GREY'], bg=COLORS['FRAME_BG'])
        header_label.grid(row=0, column=0, pady=15, sticky='w', padx=20)
        # Saving goals list
        self.saving_goals_list_frame = tk.Frame(saving_goals_frame, bg=COLORS['FRAME_BG'], relief='flat', bd=2)
        self.saving_goals_list_frame.grid(row=1, column=0, sticky='nsew', padx=20, pady=10)
        self.saving_goals_list_frame.grid_columnconfigure(0, weight=1)
        # Add saving goal form
        form_frame = tk.Frame(saving_goals_frame, bg=COLORS['FRAME_BG'], relief='flat', bd=2)
        form_frame.grid(row=2, column=0, sticky='ew', padx=20, pady=15)
        form_frame.grid_columnconfigure((0,1,2), weight=1)
        tk.Label(form_frame, text="Goal Name:", font=FONTS['FORM_LABEL'], 
                fg=COLORS['GREY'], bg=COLORS['FRAME_BG']).grid(row=0, column=0, sticky='w', pady=4, padx=8)
        self.goal_name_var = tk.StringVar()
        tk.Entry(form_frame, textvariable=self.goal_name_var, font=FONTS['FORM_LABEL'],
                bg=COLORS['WHITE'], fg=COLORS['BLACK'], relief='flat', bd=1).grid(row=1, column=0, sticky='ew', padx=(8,5), ipady=4)
        tk.Label(form_frame, text="Target Amount:", font=FONTS['FORM_LABEL'], 
                fg=COLORS['GREY'], bg=COLORS['FRAME_BG']).grid(row=0, column=1, sticky='w', pady=4, padx=8)
        self.target_amount_var = tk.StringVar()
        tk.Entry(form_frame, textvariable=self.target_amount_var, font=FONTS['FORM_LABEL'],
                bg=COLORS['WHITE'], fg=COLORS['BLACK'], relief='flat', bd=1).grid(row=1, column=1, sticky='ew', padx=(8,5), ipady=4)
        tk.Label(form_frame, text="Current Saving:", font=FONTS['FORM_LABEL'], 
                fg=COLORS['GREY'], bg=COLORS['FRAME_BG']).grid(row=0, column=2, sticky='w', pady=4, padx=8)
        self.current_saving_var = tk.StringVar()
        tk.Entry(form_frame, textvariable=self.current_saving_var, font=FONTS['FORM_LABEL'],
                bg=COLORS['WHITE'], fg=COLORS['BLACK'], relief='flat', bd=1).grid(row=1, column=2, sticky='ew', padx=(8,5), ipady=4)
        add_goal_btn = tk.Button(form_frame, text="Add Goal", font=FONTS['BUTTON'], 
                                bg=COLORS['GREEN'], fg=COLORS['BLACK'], command=self.add_saving_goal,
                                relief='flat', bd=2, padx=15, pady=6)
        add_goal_btn.grid(row=2, column=0, columnspan=3, sticky='ew', padx=8, pady=(6,8))
        delete_goal_btn = tk.Button(form_frame, text="Delete Selected", font=FONTS['BUTTON'], 
                                   bg=COLORS['RED'], fg=COLORS['WHITE'], command=self.delete_saving_goal,
                                   relief='flat', bd=2, padx=15, pady=6)
        delete_goal_btn.grid(row=3, column=0, columnspan=3, sticky='ew', padx=8, pady=(6,8))
    def setup_budgets_tab(self):
        """Setup budgets management tab"""
        budgets_frame = tk.Frame(self.notebook, bg=COLORS['FRAME_BG'])
        self.notebook.add(budgets_frame, text='Budgets')
        budgets_frame.grid_rowconfigure(1, weight=1)
        budgets_frame.grid_columnconfigure(0, weight=1)
        # Header
        header_label = tk.Label(budgets_frame, text="Budgets", font=FONTS['HEADER'], 
                               fg=COLORS['GREY'], bg=COLORS['FRAME_BG'])
        header_label.grid(row=0, column=0, pady=15, sticky='w', padx=20)
        # Budgets list
        self.budgets_list_frame = tk.Frame(budgets_frame, bg=COLORS['FRAME_BG'], relief='flat', bd=2)
        self.budgets_list_frame.grid(row=1, column=0, sticky='nsew', padx=20, pady=10)
        self.budgets_list_frame.grid_columnconfigure(0, weight=1)
        # Add budget form
        form_frame = tk.Frame(budgets_frame, bg=COLORS['FRAME_BG'], relief='flat', bd=2)
        form_frame.grid(row=2, column=0, sticky='ew', padx=20, pady=15)
        form_frame.grid_columnconfigure((0,1,2), weight=1)
        tk.Label(form_frame, text="Category:", font=FONTS['FORM_LABEL'], 
                fg=COLORS['GREY'], bg=COLORS['FRAME_BG']).grid(row=0, column=0, sticky='w', pady=4, padx=8)
        self.budget_category_combo = ttk.Combobox(form_frame, state="readonly")
        self.budget_category_combo.grid(row=1, column=0, sticky='ew', padx=(8,5), ipady=4)
        tk.Label(form_frame, text="Budget Amount:", font=FONTS['FORM_LABEL'], 
                fg=COLORS['GREY'], bg=COLORS['FRAME_BG']).grid(row=0, column=1, sticky='w', pady=4, padx=8)
        self.budget_amount_var = tk.StringVar()
        tk.Entry(form_frame, textvariable=self.budget_amount_var, font=FONTS['FORM_LABEL'],
                bg=COLORS['WHITE'], fg=COLORS['BLACK'], relief='flat', bd=1).grid(row=1, column=1, sticky='ew', padx=(8,5), ipady=4)
        tk.Label(form_frame, text="Time Period:", font=FONTS['FORM_LABEL'], 
                fg=COLORS['GREY'], bg=COLORS['FRAME_BG']).grid(row=0, column=2, sticky='w', pady=4, padx=8)
        self.time_combo = ttk.Combobox(form_frame, values=["Week", "Month", "Year"], state="readonly")
        self.time_combo.set("Month")  # Default to Month
        self.time_combo.grid(row=1, column=2, sticky='ew', padx=(8,5), ipady=4)
        add_budget_btn = tk.Button(form_frame, text="Add Budget", font=FONTS['BUTTON'], 
                                  bg=COLORS['GREEN'], fg=COLORS['BLACK'], command=self.add_budget,
                                  relief='flat', bd=2, padx=15, pady=6)
        add_budget_btn.grid(row=2, column=0, columnspan=3, sticky='ew', padx=8, pady=(6,8))
        delete_budget_btn = tk.Button(form_frame, text="Delete Selected", font=FONTS['BUTTON'], 
                                     bg=COLORS['RED'], fg=COLORS['WHITE'], command=self.delete_budget,
                                     relief='flat', bd=2, padx=15, pady=6)
        delete_budget_btn.grid(row=3, column=0, columnspan=3, sticky='ew', padx=8, pady=(6,8))
    def setup_reports_tab(self):
        """Setup reports tab"""
        reports_frame = tk.Frame(self.notebook, bg=COLORS['FRAME_BG'])
        self.notebook.add(reports_frame, text='Reports')
        reports_frame.grid_rowconfigure(1, weight=1)
        reports_frame.grid_columnconfigure(0, weight=1)
        # Header
        header_label = tk.Label(reports_frame, text="Reports", font=FONTS['HEADER'], 
                               fg=COLORS['GREY'], bg=COLORS['FRAME_BG'])
        header_label.grid(row=0, column=0, pady=15, sticky='w', padx=20)
        # Reports content
        self.setup_reports_content(reports_frame)
    def setup_reports_content(self, parent_frame):
        """Setup reports content"""
        # Main container with left panel for controls and right panel for preview
        main_container = tk.Frame(parent_frame, bg=COLORS['FRAME_BG'])
        main_container.grid(row=1, column=0, sticky='nsew', padx=20, pady=10)
        main_container.grid_rowconfigure(0, weight=1)
        main_container.grid_columnconfigure(0, weight=0)  # Controls panel
        main_container.grid_columnconfigure(1, weight=1)  # Preview panel
        # Left panel - Controls
        controls_frame = tk.Frame(main_container, bg=COLORS['FRAME_BG'], relief='solid', bd=1)
        controls_frame.grid(row=0, column=0, sticky='nsew', padx=(0,10))
        controls_frame.grid_columnconfigure(0, weight=1)
        # Controls header
        controls_header = tk.Label(controls_frame, text="Report Settings", font=FONTS['FORM_HEADER'], 
                                  fg=COLORS['GREY'], bg=COLORS['FRAME_BG'])
        controls_header.grid(row=0, column=0, pady=15, padx=15, sticky='w')
        # Report type selection
        type_label = tk.Label(controls_frame, text="Report Type:", font=FONTS['FORM_LABEL'], 
                             fg=COLORS['GREY'], bg=COLORS['FRAME_BG'])
        type_label.grid(row=1, column=0, sticky='w', padx=15, pady=(0,5))
        self.report_type_var = tk.StringVar(value="Monthly Summary")
        report_types = ["Monthly Summary", "Category Analysis", "Account Performance", "Budget vs Actual", "Complete Financial Report"]
        self.report_type_combo = ttk.Combobox(controls_frame, textvariable=self.report_type_var, 
                                             values=report_types, state="readonly", width=25)
        self.report_type_combo.grid(row=2, column=0, sticky='ew', padx=15, pady=(0,15))
        # Date range selection
        date_label = tk.Label(controls_frame, text="Date Range:", font=FONTS['FORM_LABEL'], 
                             fg=COLORS['GREY'], bg=COLORS['FRAME_BG'])
        date_label.grid(row=3, column=0, sticky='w', padx=15, pady=(0,5))
        # Preset date ranges
        self.date_range_var = tk.StringVar(value="Last 30 Days")
        date_ranges = ["Last 30 Days", "Last 3 Months", "Last 6 Months", "Last Year", "Custom Range"]
        self.date_range_combo = ttk.Combobox(controls_frame, textvariable=self.date_range_var, 
                                            values=date_ranges, state="readonly", width=25)
        self.date_range_combo.grid(row=4, column=0, sticky='ew', padx=15, pady=(0,10))
        self.date_range_combo.bind("<<ComboboxSelected>>", self.on_date_range_change)
        # Custom date range (initially hidden)
        self.custom_date_frame = tk.Frame(controls_frame, bg=COLORS['FRAME_BG'])
        self.custom_date_frame.grid(row=5, column=0, sticky='ew', padx=15, pady=(0,15))
        self.custom_date_frame.grid_columnconfigure((0,1), weight=1)
        tk.Label(self.custom_date_frame, text="From:", font=FONTS['FORM_LABEL'], 
                fg=COLORS['GREY'], bg=COLORS['FRAME_BG']).grid(row=0, column=0, sticky='w', pady=(0,5))
        self.from_date_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        self.from_date_entry = tk.Entry(self.custom_date_frame, textvariable=self.from_date_var, width=12)
        self.from_date_entry.grid(row=1, column=0, sticky='w', pady=(0,5))
        tk.Label(self.custom_date_frame, text="To:", font=FONTS['FORM_LABEL'], 
                fg=COLORS['GREY'], bg=COLORS['FRAME_BG']).grid(row=0, column=1, sticky='w', pady=(0,5))
        self.to_date_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        self.to_date_entry = tk.Entry(self.custom_date_frame, textvariable=self.to_date_var, width=12)
        self.to_date_entry.grid(row=1, column=1, sticky='w', pady=(0,5))
        # Initially hide custom date frame
        self.custom_date_frame.grid_remove()
        # Account filter
        filter_label = tk.Label(controls_frame, text="Include Accounts:", font=FONTS['FORM_LABEL'], 
                               fg=COLORS['GREY'], bg=COLORS['FRAME_BG'])
        filter_label.grid(row=6, column=0, sticky='w', padx=15, pady=(0,5))
        self.include_savings_var = tk.BooleanVar(value=True)
        savings_check = tk.Checkbutton(controls_frame, text="Savings Accounts", variable=self.include_savings_var,
                                      font=FONTS['FORM_LABEL'], fg=COLORS['GREY'], bg=COLORS['FRAME_BG'],
                                      activebackground=COLORS['FRAME_BG'], selectcolor=COLORS['WHITE'])
        savings_check.grid(row=7, column=0, sticky='w', padx=15, pady=(0,5))
        self.include_regular_var = tk.BooleanVar(value=True)
        regular_check = tk.Checkbutton(controls_frame, text="Regular Accounts", variable=self.include_regular_var,
                                      font=FONTS['FORM_LABEL'], fg=COLORS['GREY'], bg=COLORS['FRAME_BG'],
                                      activebackground=COLORS['FRAME_BG'], selectcolor=COLORS['WHITE'])
        regular_check.grid(row=8, column=0, sticky='w', padx=15, pady=(0,15))
        # Generate button
        generate_btn = tk.Button(controls_frame, text="Generate Report", font=FONTS['BUTTON'], 
                                bg=COLORS['GREEN'], fg=COLORS['BLACK'], command=self.generate_report,
                                relief='flat', bd=2, pady=10)
        generate_btn.grid(row=9, column=0, sticky='ew', padx=15, pady=(0,15))
        # Status label
        self.status_label = tk.Label(controls_frame, text="Ready to generate report", 
                                    font=FONTS['FORM_LABEL'], fg=COLORS['GREY'], bg=COLORS['FRAME_BG'])
        self.status_label.grid(row=10, column=0, sticky='ew', padx=15, pady=(0,15))
        # Right panel - Preview area
        preview_frame = tk.Frame(main_container, bg=COLORS['WHITE'], relief='solid', bd=1)
        preview_frame.grid(row=0, column=1, sticky='nsew')
        preview_frame.grid_rowconfigure(1, weight=1)
        preview_frame.grid_columnconfigure(0, weight=1)
        # Preview header
        preview_header = tk.Label(preview_frame, text="Report Preview", font=FONTS['FORM_HEADER'], 
                                 fg=COLORS['BLACK'], bg=COLORS['WHITE'])
        preview_header.grid(row=0, column=0, pady=15, sticky='w', padx=20)
        # Preview content area
        self.preview_area = tk.Frame(preview_frame, bg=COLORS['WHITE'])
        self.preview_area.grid(row=1, column=0, sticky='nsew', padx=20, pady=(0,20))
        self.preview_area.grid_columnconfigure(0, weight=1)
        # Initial preview message
        initial_msg = tk.Label(self.preview_area, text="Select report settings and click 'Generate Report' to preview", 
                              font=FONTS['LIST_ITEM'], fg=COLORS['GREY'], bg=COLORS['WHITE'])
        initial_msg.grid(row=0, column=0, pady=50)
    def on_date_range_change(self, event=None):
        """Handle date range selection change"""
        if self.date_range_var.get() == "Custom Range":
            self.custom_date_frame.grid()
        else:
            self.custom_date_frame.grid_remove()
    def get_date_range(self):
        """Get start and end dates based on selection"""
        range_type = self.date_range_var.get()
        end_date = datetime.now()
        if range_type == "Last 30 Days":
            start_date = end_date - timedelta(days=30)
        elif range_type == "Last 3 Months":
            start_date = end_date - timedelta(days=90)
        elif range_type == "Last 6 Months":
            start_date = end_date - timedelta(days=180)
        elif range_type == "Last Year":
            start_date = end_date - timedelta(days=365)
        elif range_type == "Custom Range":
            try:
                start_date = datetime.strptime(self.from_date_var.get(), "%Y-%m-%d")
                end_date = datetime.strptime(self.to_date_var.get(), "%Y-%m-%d")
            except ValueError:
                messagebox.showerror("Error", "Invalid date format. Use YYYY-MM-DD")
                return None, None
        else:
            start_date = end_date - timedelta(days=30)
        return start_date, end_date
    def generate_report(self):
        """Generate and save report"""
        try:
            self.status_label.config(text="Generating report...")
            self.parent.update()
            # Get date range
            start_date, end_date = self.get_date_range()
            if start_date is None or end_date is None:
                return
            # Get report type
            report_type = self.report_type_var.get()
            # Get filtered accounts
            accounts_to_include = []
            if self.include_regular_var.get():
                accounts_to_include.extend([acc for acc in self.accounts if acc.account_type != "Savings"])
            if self.include_savings_var.get():
                accounts_to_include.extend([acc for acc in self.accounts if acc.account_type == "Savings"])
            if not accounts_to_include:
                messagebox.showerror("Error", "Please select at least one account type to include")
                self.status_label.config(text="Ready to generate report")
                return
            # Generate report data
            report_data = self.get_report_data(start_date, end_date, accounts_to_include)
            # Create preview
            self.create_report_preview(report_data, report_type)
            self.status_label.config(text="Report generated successfully")
            messagebox.showinfo("Success", "Report generated successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate report: {str(e)}")
            self.status_label.config(text="Error generating report")
    def get_report_data(self, start_date, end_date, accounts):
        """Get comprehensive report data for the given period"""
        try:
            with self.database.get_connection() as conn:
                cursor = conn.cursor()
                # Get accounts info
                accounts_data = {}
                for account in accounts:
                    accounts_data[account.account_id] = {
                        'name': account.name,
                        'type': account.account_type,
                        'balance': account.balance
                    }
                # Get transactions
                placeholders = ','.join(['?'] * len(accounts))
                account_ids = [account.account_id for account in accounts]
                query = f"""
                    SELECT t.*, a.Name as AccountName, c.Name as CategoryName
                    FROM Transactions t
                    JOIN Account a ON t.AccountID = a.AccountID
                    LEFT JOIN Category c ON t.CategoryID = c.CategoryID
                    WHERE t.UserID = ? AND t.AccountID IN ({placeholders})
                    AND DATE(t.Date_Created) BETWEEN ? AND ?
                    ORDER BY t.Date_Created DESC
                """
                cursor.execute(query, [self.user.user_id] + account_ids + [start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')])
                transactions = []
                for row in cursor.fetchall():
                    transaction_dict = {
                        'Transaction_ID': row[0],
                        'User_ID': row[1],
                        'Account_ID': row[2],
                        'Category_ID': row[3],
                        'Amount': row[4],
                        'Description': row[5],
                        'TransactionType': row[6],
                        'To_Account_ID': row[7],
                        'Date_Created': row[8],
                        'AccountName': row[9],
                        'CategoryName': row[10]
                    }
                    transactions.append(transaction_dict)
                # Get budgets with spending for the period
                budgets = self.database.get_user_budgets_with_spending(self.user.user_id)
                # Get savings goals
                saving_goals = self.database.get_user_saving_goals(self.user.user_id)
                return {
                    'start_date': start_date,
                    'end_date': end_date,
                    'user_name': self.user.name,
                    'accounts': accounts_data,
                    'transactions': transactions,
                    'budgets': budgets,
                    'saving_goals': saving_goals
                }
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate report data: {e}")
            return None
    def create_report_preview(self, report_data, report_type):
        """Create comprehensive report preview for all report types"""
        # Clear existing preview
        for widget in self.preview_area.winfo_children():
            widget.destroy()
        # Create scrollable frame for report content
        canvas = tk.Canvas(self.preview_area, bg=COLORS['WHITE'])
        scrollbar = ttk.Scrollbar(self.preview_area, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=COLORS['WHITE'])
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        # Report header
        header_frame = tk.Frame(scrollable_frame, bg=COLORS['WHITE'])
        header_frame.pack(fill='x', padx=20, pady=(10, 20))
        title_label = tk.Label(header_frame, text=f"{report_type}", 
                              font=FONTS['HEADER'], fg=COLORS['BLACK'], bg=COLORS['WHITE'])
        title_label.pack(anchor='w')
        period_text = f"Period: {report_data['start_date'].strftime('%Y-%m-%d')} to {report_data['end_date'].strftime('%Y-%m-%d')}"
        period_label = tk.Label(header_frame, text=period_text, 
                               font=FONTS['LIST_ITEM'], fg=COLORS['GREY'], bg=COLORS['WHITE'])
        period_label.pack(anchor='w')
        # Generate content based on report type
        if report_type == "Monthly Summary":
            self._create_monthly_summary_preview(scrollable_frame, report_data)
        elif report_type == "Category Analysis":
            self._create_category_analysis_preview(scrollable_frame, report_data)
        elif report_type == "Account Performance":
            self._create_account_performance_preview(scrollable_frame, report_data)
        elif report_type == "Budget vs Actual":
            self._create_budget_analysis_preview(scrollable_frame, report_data)
        elif report_type == "Complete Financial Report":
            self._create_complete_financial_preview(scrollable_frame, report_data)
        # Enable mouse wheel scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
    def create_pdf_report(self, report_data, report_type, pdf_path):
        """Create PDF report using reportlab"""
        try:
            doc = SimpleDocTemplate(pdf_path, pagesize=letter)
            story = []
            styles = getSampleStyleSheet()
            # Custom styles
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                spaceAfter=30,
                alignment=TA_CENTER
            )
            heading_style = ParagraphStyle(
                'CustomHeading',
                parent=styles['Heading2'],
                fontSize=16,
                spaceAfter=12,
                textColor=colors.darkblue
            )
            # Title
            title_text = f"Financial Report - {report_type}"
            story.append(Paragraph(title_text, title_style))
            story.append(Spacer(1, 20))
            # Report info
            date_range = f"Period: {report_data['start_date'].strftime('%Y-%m-%d')} to {report_data['end_date'].strftime('%Y-%m-%d')}"
            story.append(Paragraph(f"User: {report_data['user_name']}", styles['Normal']))
            story.append(Paragraph(date_range, styles['Normal']))
            story.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", styles['Normal']))
            story.append(Spacer(1, 20))
            # Summary section
            story.append(Paragraph("Executive Summary", heading_style))
            total_income = sum(float(t['Amount']) for t in report_data['transactions'] if t['TransactionType'] == 'Income')
            total_expenses = sum(float(t['Amount']) for t in report_data['transactions'] if t['TransactionType'] == 'Expense')
            net_cashflow = total_income - total_expenses
            summary_data = [
                ['Metric', 'Amount (BDT)'],
                ['Total Income', f'{total_income:.2f}'],
                ['Total Expenses', f'{total_expenses:.2f}'],
                ['Net Cashflow', f'{net_cashflow:.2f}']
            ]
            summary_table = Table(summary_data, colWidths=[3*inch, 2*inch])
            summary_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(summary_table)
            story.append(Spacer(1, 20))
            # Category breakdown
            story.append(Paragraph("Category Analysis", heading_style))
            category_totals = {}
            for transaction in report_data['transactions']:
                if transaction['CategoryName']:
                    category = transaction['CategoryName']
                    amount = float(transaction['Amount'])
                    trans_type = transaction['TransactionType']
                    if category not in category_totals:
                        category_totals[category] = {'Income': 0, 'Expense': 0}
                    category_totals[category][trans_type] += amount
            if category_totals:
                category_data = [['Category', 'Income (BDT)', 'Expenses (BDT)', 'Net (BDT)']]
                for category, amounts in category_totals.items():
                    net = amounts['Income'] - amounts['Expense']
                    category_data.append([
                        category,
                        f"{amounts['Income']:.2f}",
                        f"{amounts['Expense']:.2f}",
                        f"{net:.2f}"
                    ])
                category_table = Table(category_data, colWidths=[2*inch, 1.5*inch, 1.5*inch, 1.5*inch])
                category_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 11),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                story.append(category_table)
            else:
                story.append(Paragraph("No categorized transactions found.", styles['Normal']))
            story.append(Spacer(1, 20))
            # Account summary
            story.append(Paragraph("Account Summary", heading_style))
            account_data = [['Account', 'Type', 'Current Balance (BDT)']]
            for account_id, account_info in report_data['accounts'].items():
                account_data.append([
                    account_info['name'],
                    account_info['type'],
                    f"{account_info['balance']:.2f}"
                ])
            account_table = Table(account_data, colWidths=[3*inch, 1.5*inch, 2*inch])
            account_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(account_table)
            story.append(Spacer(1, 20))
            # Recent transactions (last 10)
            story.append(Paragraph("Recent Transactions", heading_style))
            recent_transactions = report_data['transactions'][:10]  # Already sorted by date DESC
            if recent_transactions:
                trans_data = [['Date', 'Description', 'Category', 'Amount (BDT)', 'Type']]
                for trans in recent_transactions:
                    date_str = trans['Date_Created'][:10]  # Get date part
                    amount_str = f"{float(trans['Amount']):.2f}"
                    if trans['TransactionType'] == 'Expense':
                        amount_str = f"-{amount_str}"
                    elif trans['TransactionType'] == 'Income':
                        amount_str = f"+{amount_str}"
                    trans_data.append([
                        date_str,
                        trans['Description'] or 'No description',
                        trans['CategoryName'] or 'Transfer',
                        amount_str,
                        trans['TransactionType']
                    ])
                trans_table = Table(trans_data, colWidths=[1*inch, 2*inch, 1.5*inch, 1*inch, 1*inch])
                trans_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (2, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('FONTSIZE', (0, 1), (-1, -1), 9),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                story.append(trans_table)
            else:
                story.append(Paragraph("No transactions found in the selected period.", styles['Normal']))
            # Create charts and add to PDF
            self.add_charts_to_pdf(story, report_data, report_type)
            # Build PDF
            doc.build(story)
        except Exception as e:
            raise
    def add_charts_to_pdf(self, story, report_data, report_type):
        """Add charts to PDF report"""
        try:
            # Create temporary directory for chart images
            temp_dir = tempfile.mkdtemp()
            # Income vs Expenses chart
            fig, ax = plt.subplots(figsize=(8, 5))
            income = sum(float(t['Amount']) for t in report_data['transactions'] if t['TransactionType'] == 'Income')
            expenses = sum(float(t['Amount']) for t in report_data['transactions'] if t['TransactionType'] == 'Expense')
            categories = ['Income', 'Expenses']
            amounts = [income, expenses]
            colors_list = ['#00FF7F', '#FF6B6B']
            bars = ax.bar(categories, amounts, color=colors_list, alpha=0.8)
            ax.set_title('Income vs Expenses Comparison', fontsize=14, fontweight='bold')
            ax.set_ylabel('Amount (BDT)', fontsize=12)
            # Add value labels on bars
            for bar, amount in zip(bars, amounts):
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{amount:.2f}', ha='center', va='bottom', fontsize=11)
            # Save chart
            chart1_path = os.path.join(temp_dir, 'income_vs_expenses.png')
            plt.savefig(chart1_path, dpi=150, bbox_inches='tight', facecolor='white')
            plt.close()
            # Add chart to PDF
            story.append(Spacer(1, 20))
            story.append(Paragraph("Income vs Expenses Analysis", getSampleStyleSheet()['Heading2']))
            story.append(Spacer(1, 10))
            story.append(Image(chart1_path, width=6*inch, height=3.75*inch))
            # Category pie chart if there are expenses
            category_totals = {}
            for transaction in report_data['transactions']:
                if transaction['TransactionType'] == 'Expense' and transaction['CategoryName']:
                    category = transaction['CategoryName']
                    amount = float(transaction['Amount'])
                    category_totals[category] = category_totals.get(category, 0) + amount
            if category_totals:
                fig, ax = plt.subplots(figsize=(8, 6))
                categories = list(category_totals.keys())
                amounts = list(category_totals.values())
                # Create pie chart
                wedges, texts, autotexts = ax.pie(amounts, labels=categories, autopct='%1.1f%%', 
                                                 startangle=90, textprops={'fontsize': 10})
                ax.set_title('Expense Distribution by Category', fontsize=14, fontweight='bold')
                # Save chart
                chart2_path = os.path.join(temp_dir, 'category_breakdown.png')
                plt.savefig(chart2_path, dpi=150, bbox_inches='tight', facecolor='white')
                plt.close()
                # Add chart to PDF
                story.append(Spacer(1, 20))
                story.append(Paragraph("Expense Breakdown by Category", getSampleStyleSheet()['Heading2']))
                story.append(Spacer(1, 10))
                story.append(Image(chart2_path, width=6*inch, height=4.5*inch))
            # Clean up temporary files
            try:
                import shutil
                shutil.rmtree(temp_dir)
            except:
                pass  # Ignore cleanup errors
        except Exception as e:
            # Continue without charts if there's an error
            pass
    
    def refresh_data(self):
        """Refresh all data from database"""
        # Get updated data
        self.accounts = self.database.get_user_accounts(self.user.user_id)
        self.categories = self.database.get_user_categories(self.user.user_id)
        self.saving_goals = self.database.get_user_saving_goals(self.user.user_id)
        self.budgets = self.database.get_user_budgets_with_spending(self.user.user_id)
        # Get balance summary
        summary = self.database.get_user_balance_summary(self.user.user_id)
        # Update balance display
        self.balance_label.config(text=f"{summary['total_balance']:.2f} BDT")
        self.income_value_label.config(text=f"{summary['monthly_income']:.2f} BDT")
        self.expense_value_label.config(text=f"{summary['monthly_expense']:.2f} BDT")
        self.cashflow_label.config(text=f"{summary['monthly_cashflow']:.2f} BDT")
        # Refresh lists
        self.refresh_accounts_list()
        self.refresh_categories_list()
        self.refresh_saving_goals_list()
        self.refresh_budgets_list()
        self.display_transactions()
        # Update budget category dropdown with expense categories
        expense_categories = [c for c in self.categories if c.category_type == "Expense"]
        category_names = [cat.name for cat in expense_categories]
        if hasattr(self, 'budget_category_combo'):
            self.budget_category_combo['values'] = category_names
        # Refresh saving goals and budgets
        self.refresh_saving_goals()
        self.refresh_budgets()
    def refresh_accounts_list(self):
        """Refresh accounts list display"""
        for widget in self.accounts_list_frame.winfo_children():
            widget.destroy()
        for i, account in enumerate(self.accounts):
            color = COLORS['GREEN'] if i == self.selected_account_index else COLORS['GREY']
            account_btn = tk.Button(self.accounts_list_frame, 
                                   text=f"{account.name}\n{account.balance:.2f} BDT • {account.account_type}", 
                                   font=FONTS['LIST_ITEM'], bg=color, fg=COLORS['BLACK'],
                                   relief='flat', bd=2, pady=10, anchor='w', justify='left',
                                   command=lambda idx=i: self.select_account(idx))
            account_btn.grid(row=i, column=0, sticky='ew', pady=2, padx=4)
    def refresh_categories_list(self):
        """Refresh categories list display"""
        for widget in self.categories_list_frame.winfo_children():
            widget.destroy()
        for i, category in enumerate(self.categories):
            color = COLORS['GREEN'] if i == self.selected_category_index else (
                COLORS['GREY'] if category.category_type == "Expense" else COLORS['LIGHT_GREEN'])
            category_btn = tk.Button(self.categories_list_frame, 
                                    text=f"{category.name} ({category.category_type})", 
                                    font=FONTS['LIST_ITEM'], bg=color, fg=COLORS['BLACK'],
                                    relief='flat', bd=2, pady=8, anchor='w',
                                    command=lambda idx=i: self.select_category(idx))
            category_btn.grid(row=i, column=0, sticky='ew', pady=2, padx=4)
    def refresh_saving_goals_list(self):
        """Refresh saving goals list display"""
        for widget in self.saving_goals_list_frame.winfo_children():
            widget.destroy()
        if not self.saving_goals:
            no_goals_label = tk.Label(self.saving_goals_list_frame, 
                                     text="No saving goals yet.\nCreate one using the form below!", 
                                     font=FONTS['LIST_ITEM'], fg=COLORS['GREY'], bg=COLORS['FRAME_BG'],
                                     justify='center')
            no_goals_label.grid(row=0, column=0, sticky='ew', pady=20, padx=4)
            return
        for i, goal in enumerate(self.saving_goals):
            color = COLORS['GREEN'] if i == self.selected_saving_goal_index else COLORS['GREY']
            # Create goal display text
            if goal.is_default:
                goal_text = f"{goal.goal_name}\nCurrent: {goal.current_amount:.2f} BDT"
            else:
                progress_pct = goal.progress_percentage()
                goal_text = f"{goal.goal_name}\n{goal.current_amount:.2f} / {goal.target_amount:.2f} BDT ({progress_pct:.1f}%)"
            goal_btn = tk.Button(self.saving_goals_list_frame, 
                                text=goal_text,
                                font=FONTS['LIST_ITEM'], bg=color, fg=COLORS['BLACK'],
                                relief='flat', bd=2, pady=10, anchor='w', justify='left',
                                command=lambda idx=i: self.select_saving_goal(idx))
            goal_btn.grid(row=i, column=0, sticky='ew', pady=2, padx=4)
    def refresh_budgets_list(self):
        """Refresh budgets list display"""
        for widget in self.budgets_list_frame.winfo_children():
            widget.destroy()
        for i, budget in enumerate(self.budgets):
            color = COLORS['GREEN'] if i == self.selected_budget_index else (
                COLORS['RED'] if budget['is_over_threshold'] else COLORS['GREY'])
            budget_text = f"{budget['category_name']} - {budget['time_period']}\n{budget['spent_amount']:.2f} / {budget['budget_amount']:.2f} BDT"
            budget_btn = tk.Button(self.budgets_list_frame, 
                                  text=budget_text,
                                  font=FONTS['LIST_ITEM'], bg=color, fg=COLORS['BLACK'],
                                  relief='flat', bd=2, pady=10, anchor='w', justify='left',
                                  command=lambda idx=i: self.select_budget(idx))
            budget_btn.grid(row=i, column=0, sticky='ew', pady=2, padx=4)
    def get_category_total_spent(self, category_id):
        """Get total amount spent in a category"""
        try:
            with self.database.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT SUM(Amount) as total FROM Transactions 
                    WHERE CategoryID = ? AND TransactionType = 'Expense'
                """, (category_id,))
                result = cursor.fetchone()
                return result['total'] or 0.0
        except Exception:
            return 0.0
    def select_account(self, index):
        """Select an account"""
        self.selected_account_index = index
        self.refresh_accounts_list()
    def select_category(self, index):
        """Select a category"""
        self.selected_category_index = index
        self.refresh_categories_list()
    def select_saving_goal(self, index):
        """Select a saving goal"""
        self.selected_saving_goal_index = index
        self.refresh_saving_goals_list()
    def select_budget(self, index):
        """Select a budget"""
        self.selected_budget_index = index
        self.refresh_budgets_list()
    def add_account(self):
        """Add a new account"""
        name = self.account_name_var.get().strip()
        account_type = self.account_type_combo.get()
        if not name or not account_type:
            messagebox.showerror("Error", "Please fill all fields")
            return
        try:
            account = Account(user_id=self.user.user_id, name=name, account_type=account_type)
            self.database.create_account(account)
            self.account_name_var.set("")
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
        if messagebox.askyesno("Confirm Delete", f"Delete account '{account.name}'?"):
            try:
                self.database.delete_account(account.account_id, self.user.user_id)
                self.selected_account_index = -1
                self.refresh_data()
            except DatabaseError as e:
                messagebox.showerror("Database Error", str(e))
    def add_category(self):
        """Add a new category"""
        name = self.category_name_var.get().strip()
        category_type = self.category_type_combo.get()
        if not name or not category_type:
            messagebox.showerror("Error", "Please fill all fields")
            return
        try:
            category = Category(user_id=self.user.user_id, name=name, category_type=category_type)
            self.database.create_category(category)
            self.category_name_var.set("")
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
        if messagebox.askyesno("Confirm Delete", f"Delete category '{category.name}'?"):
            try:
                self.database.delete_category(category.category_id, self.user.user_id)
                self.selected_category_index = -1
                self.refresh_data()
            except DatabaseError as e:
                messagebox.showerror("Database Error", str(e))
    def open_income_popup(self):
        """Open income popup"""
        if not self.accounts:
            messagebox.showerror("Error", "Please add at least one account first")
            return
        IncomePopup(self.parent, self.database, self.user, self.accounts, self.categories, self.refresh_data)
    def open_expense_popup(self):
        """Open expense popup"""
        # Filter out savings accounts for expense transactions
        non_savings_accounts = [acc for acc in self.accounts if acc.account_type != "Savings"]
        if not non_savings_accounts:
            messagebox.showerror("Error", "Please add at least one non-savings account first")
            return
        ExpensePopup(self.parent, self.database, self.user, non_savings_accounts, self.categories, self.refresh_data)
    def open_transfer_popup(self):
        """Open transfer popup"""
        if len(self.accounts) < 2:
            messagebox.showerror("Error", "Please add at least two accounts first")
            return
        TransferPopup(self.parent, self.database, self.user, self.accounts, self.refresh_data)
    def setup_saving_goals_tracker(self, parent_frame):
        """Setup saving goals tracker in top right quadrant"""
        parent_frame.grid_rowconfigure(0, weight=1)  # Goals list
        parent_frame.grid_rowconfigure(1, weight=0)  # Pagination controls
        parent_frame.grid_rowconfigure(2, weight=0)  # Add button
        parent_frame.grid_columnconfigure(0, weight=1)
        # Goals list frame
        self.goals_list_frame = tk.Frame(parent_frame, bg=COLORS['FRAME_BG'], relief='flat', bd=1)
        self.goals_list_frame.grid(row=0, column=0, sticky='nsew', padx=8, pady=8)
        self.goals_list_frame.grid_columnconfigure(0, weight=1)
        # Pagination variables for saving goals
        self.goals_current_page = 0
        self.goals_items_per_page = 3
        self.goals_total_pages = 1
        # Pagination controls for goals
        goals_pagination_frame = tk.Frame(parent_frame, bg=COLORS['FRAME_BG'], relief='flat', bd=1)
        goals_pagination_frame.grid(row=1, column=0, sticky="ew", padx=8, pady=(0,4))
        goals_pagination_frame.grid_columnconfigure(1, weight=1)
        self.goals_prev_btn = tk.Button(goals_pagination_frame, text="Previous", font=('inter', 10, 'normal'), 
                                       bg=COLORS['GREY'], fg=COLORS['BLACK'], command=self.prev_goals_page, 
                                       relief='flat', bd=1, padx=12, pady=4)
        self.goals_prev_btn.grid(row=0, column=0, padx=6, pady=4)
        self.goals_page_label = tk.Label(goals_pagination_frame, text="Page 1 of 1", 
                                        font=('inter', 10, 'normal'), fg=COLORS['GREY'], bg=COLORS['FRAME_BG'])
        self.goals_page_label.grid(row=0, column=1, pady=4)
        self.goals_next_btn = tk.Button(goals_pagination_frame, text="Next", font=('inter', 10, 'normal'), 
                                       bg=COLORS['GREY'], fg=COLORS['BLACK'], command=self.next_goals_page, 
                                       relief='flat', bd=1, padx=12, pady=4)
        self.goals_next_btn.grid(row=0, column=2, padx=6, pady=4)
        # Add Saving Goal button
        add_goal_btn = tk.Button(parent_frame, text="Add Saving Goal", 
                                font=FONTS['BUTTON'], bg=COLORS['GREEN'], 
                                fg=COLORS['BLACK'], command=self.open_saving_goal_popup,
                                relief='flat', bd=2, pady=6)
        add_goal_btn.grid(row=2, column=0, sticky='ew', padx=8, pady=(0,8))
    def setup_budget_tracker(self, parent_frame):
        """Setup budget tracker in bottom right quadrant"""
        parent_frame.grid_rowconfigure(0, weight=0)  # Table headers
        parent_frame.grid_rowconfigure(1, weight=1)  # Budget list
        parent_frame.grid_rowconfigure(2, weight=0)  # Pagination controls
        parent_frame.grid_rowconfigure(3, weight=0)  # Add button
        parent_frame.grid_columnconfigure(0, weight=1)
        # Table headers
        headers_frame = tk.Frame(parent_frame, bg=COLORS['FRAME_BG'], relief='flat', bd=1)
        headers_frame.grid(row=0, column=0, sticky='ew', padx=8, pady=(8,2))
        headers_frame.grid_columnconfigure((0,1,2,3), weight=1)
        tk.Label(headers_frame, text="Category", font=FONTS['BUTTON'], 
                fg=COLORS['GREY'], bg=COLORS['FRAME_BG']).grid(
                row=0, column=0, sticky='ew', padx=2, pady=4, ipady=3)
        tk.Label(headers_frame, text="Budget", font=FONTS['BUTTON'], 
                fg=COLORS['GREY'], bg=COLORS['FRAME_BG']).grid(
                row=0, column=1, sticky='ew', padx=2, pady=4, ipady=3)
        tk.Label(headers_frame, text="Remaining", font=FONTS['BUTTON'], 
                fg=COLORS['GREY'], bg=COLORS['FRAME_BG']).grid(
                row=0, column=2, sticky='ew', padx=2, pady=4, ipady=3)
        tk.Label(headers_frame, text="Spent", font=FONTS['BUTTON'], 
                fg=COLORS['GREY'], bg=COLORS['FRAME_BG']).grid(
                row=0, column=3, sticky='ew', padx=2, pady=4, ipady=3)
        # Budget list frame
        self.budget_list_frame = tk.Frame(parent_frame, bg=COLORS['FRAME_BG'], relief='flat', bd=1)
        self.budget_list_frame.grid(row=1, column=0, sticky='nsew', padx=8, pady=2)
        self.budget_list_frame.grid_columnconfigure((0,1,2,3), weight=1)
        # Pagination variables for budgets
        self.budgets_current_page = 0
        self.budgets_items_per_page = 5
        self.budgets_total_pages = 1
        # Pagination controls for budgets
        budgets_pagination_frame = tk.Frame(parent_frame, bg=COLORS['FRAME_BG'], relief='flat', bd=1)
        budgets_pagination_frame.grid(row=2, column=0, sticky="ew", padx=8, pady=(2,4))
        budgets_pagination_frame.grid_columnconfigure(1, weight=1)
        self.budgets_prev_btn = tk.Button(budgets_pagination_frame, text="Previous", font=('inter', 10, 'normal'), 
                                         bg=COLORS['GREY'], fg=COLORS['BLACK'], command=self.prev_budgets_page, 
                                         relief='flat', bd=1, padx=12, pady=4)
        self.budgets_prev_btn.grid(row=0, column=0, padx=6, pady=4)
        self.budgets_page_label = tk.Label(budgets_pagination_frame, text="Page 1 of 1", 
                                          font=('inter', 10, 'normal'), fg=COLORS['GREY'], bg=COLORS['FRAME_BG'])
        self.budgets_page_label.grid(row=0, column=1, pady=4)
        self.budgets_next_btn = tk.Button(budgets_pagination_frame, text="Next", font=('inter', 10, 'normal'), 
                                         bg=COLORS['GREY'], fg=COLORS['BLACK'], command=self.next_budgets_page, 
                                         relief='flat', bd=1, padx=12, pady=4)
        self.budgets_next_btn.grid(row=0, column=2, padx=6, pady=4)
        # Add Budget button
        add_budget_btn = tk.Button(parent_frame, text="Add Budget", 
                                  font=FONTS['BUTTON'], bg=COLORS['GREEN'], 
                                  fg=COLORS['BLACK'], command=self.open_budget_popup,
                                  relief='flat', bd=2, pady=6)
        add_budget_btn.grid(row=3, column=0, sticky='ew', padx=8, pady=(0,8))
    def refresh_saving_goals(self):
        """Refresh saving goals display with pagination"""
        # Clear existing goals
        for widget in self.goals_list_frame.winfo_children():
            widget.destroy()
        # Get all saving goals
        all_goals = self.database.get_user_saving_goals(self.user.user_id)
        if not all_goals:
            no_goals_label = tk.Label(self.goals_list_frame, 
                                     text="No saving goals yet.\nClick 'Add Saving Goal' to start!", 
                                     font=('inter', 11, 'normal'), fg=COLORS['GREY'], bg=COLORS['FRAME_BG'],
                                     justify='center')
            no_goals_label.grid(row=0, column=0, sticky='ew', pady=20, padx=4)
            # Update pagination
            self.goals_total_pages = 1
            self.goals_current_page = 0
            self.goals_prev_btn.config(state="disabled")
            self.goals_next_btn.config(state="disabled")
            self.goals_page_label.config(text="Page 1 of 1")
            return
        # Calculate pagination
        self.goals_total_pages = max(1, (len(all_goals) + self.goals_items_per_page - 1) // self.goals_items_per_page)
        # Ensure current page is within bounds
        if self.goals_current_page >= self.goals_total_pages:
            self.goals_current_page = max(0, self.goals_total_pages - 1)
        start_idx = self.goals_current_page * self.goals_items_per_page
        end_idx = min(start_idx + self.goals_items_per_page, len(all_goals))
        page_goals = all_goals[start_idx:end_idx]
        for i, goal in enumerate(page_goals):
            goal_frame = tk.Frame(self.goals_list_frame, bg=COLORS['GREY'], relief='flat', bd=2)
            goal_frame.grid(row=i, column=0, sticky='ew', pady=3, padx=4)
            goal_frame.grid_columnconfigure(0, weight=1)
            # Goal name and progress
            name_label = tk.Label(goal_frame, text=goal.goal_name, 
                                 font=('inter', 12, 'bold'), fg=COLORS['BLACK'], bg=COLORS['GREY'])
            name_label.grid(row=0, column=0, sticky='w', padx=8, pady=(6,0))
            # Progress info
            if goal.is_default:
                # Default goal - no progress bar
                amount_text = f"{goal.current_amount:.2f} BDT"
            else:
                progress_pct = goal.progress_percentage()
                amount_text = f"{goal.current_amount:.2f} / {goal.target_amount:.2f} BDT"
                # Progress bar - only show if target amount > 0
                if goal.target_amount > 0:
                    progress_frame = tk.Frame(goal_frame, bg=COLORS['GREY'])
                    progress_frame.grid(row=1, column=0, sticky='ew', padx=8, pady=2)
                    progress_frame.grid_columnconfigure(0, weight=1)
                    progress_bg = tk.Frame(progress_frame, bg=COLORS['FRAME_BG'], height=8, relief='flat', bd=1)
                    progress_bg.grid(row=0, column=0, sticky='ew')
                    if progress_pct > 0:
                        # Ensure progress doesn't exceed 100%
                        display_pct = min(progress_pct, 100.0)
                        progress_fill = tk.Frame(progress_bg, bg=COLORS['GREEN'], height=6)
                        progress_fill.place(x=1, y=1, relwidth=display_pct/100, relheight=0.75)
            amount_label = tk.Label(goal_frame, text=amount_text, 
                                   font=('inter', 10, 'normal'), fg=COLORS['BLACK'], bg=COLORS['GREY'])
            amount_label.grid(row=2, column=0, sticky='w', padx=8, pady=(0,6))
            # Check if goal is completed
            if not goal.is_default and goal.is_completed():
                self.show_goal_completion_celebration(goal)
        # Update pagination buttons
        self.goals_prev_btn.config(state="normal" if self.goals_current_page > 0 else "disabled")
        self.goals_next_btn.config(state="normal" if self.goals_current_page < self.goals_total_pages - 1 else "disabled")
        self.goals_page_label.config(text=f"Page {self.goals_current_page + 1} of {self.goals_total_pages}")
    def refresh_budgets(self):
        """Refresh budget tracker display with pagination"""
        # Clear existing budgets
        for widget in self.budget_list_frame.winfo_children():
            widget.destroy()
        # Clean up expired budgets first
        self.database.cleanup_expired_budgets(self.user.user_id)
        # Get all budgets with spending
        all_budgets = self.database.get_user_budgets_with_spending(self.user.user_id)
        if not all_budgets:
            no_budgets_label = tk.Label(self.budget_list_frame, 
                                       text="No budgets yet.\nClick 'Add Budget' to start!", 
                                       font=('inter', 11, 'normal'), fg=COLORS['GREY'], bg=COLORS['FRAME_BG'],
                                       justify='center')
            no_budgets_label.grid(row=0, column=0, columnspan=4, sticky='ew', pady=20, padx=4)
            # Update pagination
            self.budgets_total_pages = 1
            self.budgets_current_page = 0
            self.budgets_prev_btn.config(state="disabled")
            self.budgets_next_btn.config(state="disabled")
            self.budgets_page_label.config(text="Page 1 of 1")
            return
        # Calculate pagination
        self.budgets_total_pages = max(1, (len(all_budgets) + self.budgets_items_per_page - 1) // self.budgets_items_per_page)
        start_idx = self.budgets_current_page * self.budgets_items_per_page
        end_idx = min(start_idx + self.budgets_items_per_page, len(all_budgets))
        page_budgets = all_budgets[start_idx:end_idx]
        for i, budget in enumerate(page_budgets):
            # Determine text color based on spending threshold
            text_color = COLORS['GREY']
            row_bg = COLORS['FRAME_BG']
            # Create budget row
            tk.Label(self.budget_list_frame, text=budget['category_name'], 
                    font=('inter', 10, 'normal'), fg=text_color, bg=row_bg).grid(
                    row=i, column=0, sticky='ew', padx=1, pady=1, ipady=3)
            tk.Label(self.budget_list_frame, text=f"{budget['budget_amount']:.2f}", 
                    font=('inter', 10, 'normal'), fg=text_color, bg=row_bg).grid(
                    row=i, column=1, sticky='ew', padx=1, pady=1, ipady=3)
            # Remaining amount - red if over threshold
            remaining_color = COLORS['RED'] if budget['is_over_threshold'] else text_color
            tk.Label(self.budget_list_frame, text=f"{budget['remaining_amount']:.2f}", 
                    font=('inter', 10, 'normal'), fg=remaining_color, bg=row_bg).grid(
                    row=i, column=2, sticky='ew', padx=1, pady=1, ipady=3)
            tk.Label(self.budget_list_frame, text=f"{budget['spent_amount']:.2f}", 
                    font=('inter', 10, 'normal'), fg=text_color, bg=row_bg).grid(
                    row=i, column=3, sticky='ew', padx=1, pady=1, ipady=3)
        # Update pagination buttons
        self.budgets_prev_btn.config(state="normal" if self.budgets_current_page > 0 else "disabled")
        self.budgets_next_btn.config(state="normal" if self.budgets_current_page < self.budgets_total_pages - 1 else "disabled")
        self.budgets_page_label.config(text=f"Page {self.budgets_current_page + 1} of {self.budgets_total_pages}")
    def show_goal_completion_celebration(self, goal):
        """Show celebration popup for completed goal"""
        # Check if we've already shown celebration for this goal
        if hasattr(self, '_celebrated_goals') and goal.goal_id in self._celebrated_goals:
            return
        # Mark this goal as celebrated
        if not hasattr(self, '_celebrated_goals'):
            self._celebrated_goals = set()
        self._celebrated_goals.add(goal.goal_id)
        celebration_popup = tk.Toplevel(self.parent)
        celebration_popup.title("🎉 Goal Completed! 🎉")
        celebration_popup.geometry("500x300")
        celebration_popup.configure(bg=COLORS['GREEN'])
        celebration_popup.grab_set()
        celebration_popup.transient(self.parent)
        # Center the popup
        celebration_popup.update_idletasks()
        x = (celebration_popup.winfo_screenwidth() // 2) - (250)
        y = (celebration_popup.winfo_screenheight() // 2) - (150)
        celebration_popup.geometry(f"500x300+{x}+{y}")
        # Celebration content
        celebration_label = tk.Label(celebration_popup, 
                                    text=f"🎉🎊 CONGRATULATIONS! 🎊🎉\n\nYou've completed your goal:\n'{goal.goal_name}'\n\nAmount achieved: {goal.current_amount:.2f} BDT", 
                                    font=('inter', 16, 'bold'), fg=COLORS['BLACK'], bg=COLORS['GREEN'],
                                    justify='center')
        celebration_label.pack(expand=True, pady=20)
        # Options frame
        options_frame = tk.Frame(celebration_popup, bg=COLORS['GREEN'])
        options_frame.pack(pady=20)
        # Keep as normal account button
        keep_btn = tk.Button(options_frame, text="Keep as Normal Account", 
                            font=('inter', 12, 'bold'), bg=COLORS['WHITE'], fg=COLORS['BLACK'],
                            command=lambda: self.convert_to_normal_account(goal, celebration_popup),
                            padx=20, pady=10)
        keep_btn.pack(side='left', padx=10)
        # Close button (keep as savings goal)
        close_btn = tk.Button(options_frame, text="Keep as Savings Goal", 
                             font=('inter', 12, 'bold'), bg=COLORS['GREY'], fg=COLORS['BLACK'],
                             command=celebration_popup.destroy,
                             padx=20, pady=10)
        close_btn.pack(side='right', padx=10)
    def convert_to_normal_account(self, goal, popup):
        """Convert saving account to normal bank account"""
        try:
            # Get the account and update its type to Bank
            with self.database.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE Account SET AccountType = 'Bank', Name = ? 
                    WHERE AccountID = ?
                """, (f"{goal.goal_name} Account", goal.account_id))
                # Delete the saving goal
                cursor.execute("DELETE FROM SavingGoal WHERE GoalID = ?", (goal.goal_id,))
                conn.commit()
            popup.destroy()
            messagebox.showinfo("Success", f"'{goal.goal_name}' converted to a normal bank account!")
            self.refresh_data()
        except DatabaseError as e:
            messagebox.showerror("Error", str(e))
    def delete_completed_goal(self, goal, popup):
        """Delete completed saving goal and account"""
        try:
            self.database.delete_saving_goal(goal.goal_id, self.user.user_id)
            popup.destroy()
            messagebox.showinfo("Success", "Saving goal and account deleted!")
            self.refresh_data()
        except DatabaseError as e:
            messagebox.showerror("Error", str(e))
    def open_saving_goal_popup(self):
        """Open saving goal creation popup"""
        SavingGoalPopup(self.parent, self.database, self.user, self.refresh_data)
    def open_budget_popup(self):
        """Open budget creation popup"""
        if not self.categories:
            messagebox.showerror("Error", "Please add expense categories first")
            return
        BudgetPopup(self.parent, self.database, self.user, self.categories, self.refresh_data)
    def navigate_page(self, page_type, direction):
        """Generic method to navigate pages"""
        if page_type == "goals":
            if direction == "prev" and self.goals_current_page > 0:
                self.goals_current_page -= 1
                self.refresh_saving_goals()
            elif direction == "next" and self.goals_current_page < self.goals_total_pages - 1:
                self.goals_current_page += 1
                self.refresh_saving_goals()
        elif page_type == "budgets":
            if direction == "prev" and self.budgets_current_page > 0:
                self.budgets_current_page -= 1
                self.refresh_budgets()
            elif direction == "next" and self.budgets_current_page < self.budgets_total_pages - 1:
                self.budgets_current_page += 1
                self.refresh_budgets()
    # Convenience methods
    def prev_goals_page(self):
        self.navigate_page("goals", "prev")
    def next_goals_page(self):
        self.navigate_page("goals", "next")
    def prev_budgets_page(self):
        self.navigate_page("budgets", "prev")
    def next_budgets_page(self):
        self.navigate_page("budgets", "next")
    def add_saving_goal(self):
        """Add a new saving goal"""
        goal_name = self.goal_name_var.get().strip()
        target_amount_str = self.target_amount_var.get().strip()
        current_saving_str = self.current_saving_var.get().strip()
        if not goal_name:
            messagebox.showerror("Error", "Please enter a goal name")
            return
        try:
            # Validate target amount
            target_amount = float(target_amount_str) if target_amount_str else 0.0
            if target_amount < 0:
                messagebox.showerror("Error", "Target amount cannot be negative")
                return
            # Validate current amount
            current_amount = float(current_saving_str) if current_saving_str else 0.0
            if current_amount < 0:
                messagebox.showerror("Error", "Current saving amount cannot be negative")
                return
            # Warning if current exceeds target
            if target_amount > 0 and current_amount > target_amount:
                if not messagebox.askyesno("Warning", 
                    f"Current saving ({current_amount:.2f}) exceeds target ({target_amount:.2f}). Continue?"):
                    return
            # Create saving goal
            goal = SavingGoal(
                user_id=self.user.user_id,
                goal_name=goal_name,
                target_amount=target_amount,
                current_amount=current_amount
            )
            self.database.create_saving_goal(goal)
            # Clear form
            self.goal_name_var.set("")
            self.target_amount_var.set("")
            self.current_saving_var.set("")
            messagebox.showinfo("Success", f"Saving goal '{goal_name}' created successfully!")
            self.refresh_data()
        except ValueError:
            messagebox.showerror("Error", "Please enter valid amounts")
        except ValidationError as e:
            messagebox.showerror("Validation Error", str(e))
        except DatabaseError as e:
            messagebox.showerror("Database Error", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create saving goal: {e}")
    def delete_saving_goal(self):
        """Delete selected saving goal"""
        if self.selected_saving_goal_index == -1:
            messagebox.showerror("Error", "Please select a saving goal to delete")
            return
        goal = self.saving_goals[self.selected_saving_goal_index]
        if messagebox.askyesno("Confirm Delete", f"Delete saving goal '{goal.goal_name}'?"):
            try:
                self.database.delete_saving_goal(goal.goal_id, self.user.user_id)
                self.selected_saving_goal_index = -1
                self.refresh_data()
            except DatabaseError as e:
                messagebox.showerror("Database Error", str(e))
    def add_budget(self):
        """Add a new budget"""
        category_index = self.budget_category_combo.current()
        budget_amount_str = self.budget_amount_var.get().strip()
        time_period = self.time_combo.get()
        if category_index == -1:
            messagebox.showerror("Error", "Please select a category")
            return
        if not budget_amount_str:
            messagebox.showerror("Error", "Please enter a budget amount")
            return
        if not time_period:
            messagebox.showerror("Error", "Please select a time period")
            return
        try:
            budget_amount = float(budget_amount_str)
            # Get expense categories for the budget
            expense_categories = [c for c in self.categories if c.category_type == "Expense"]
            if category_index >= len(expense_categories):
                messagebox.showerror("Error", "Invalid category selection")
                return
            category = expense_categories[category_index]
            # Create budget
            budget = Budget(
                user_id=self.user.user_id,
                category_id=category.category_id,
                budget_amount=budget_amount,
                time_period=time_period
            )
            self.database.create_budget(budget)
            self.budget_amount_var.set("")
            self.budget_category_combo.set("")
            self.time_combo.set("Month")
            self.refresh_data()
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid budget amount")
        except ValidationError as e:
            messagebox.showerror("Validation Error", str(e))
        except DatabaseError as e:
            messagebox.showerror("Database Error", str(e))
    def delete_budget(self):
        """Delete selected budget"""
        if self.selected_budget_index == -1:
            messagebox.showerror("Error", "Please select a budget to delete")
            return
        budget = self.budgets[self.selected_budget_index]
        if messagebox.askyesno("Confirm Delete", f"Delete budget for '{budget['category_name']}'?"):
            try:
                self.database.delete_budget(budget['budget_id'], self.user.user_id)
                self.selected_budget_index = -1
                self.refresh_data()
            except DatabaseError as e:
                messagebox.showerror("Database Error", str(e))
    def _create_monthly_summary_preview(self, parent_frame, report_data):
        """Create monthly summary report preview"""
        # Calculate summary statistics
        total_income = sum(float(t['Amount']) for t in report_data['transactions'] if t['TransactionType'] == 'Income')
        total_expenses = sum(float(t['Amount']) for t in report_data['transactions'] if t['TransactionType'] == 'Expense')
        net_cashflow = total_income - total_expenses
        # Summary cards
        summary_frame = tk.Frame(parent_frame, bg=COLORS['WHITE'])
        summary_frame.pack(fill='x', padx=20, pady=(0,20))
        summary_frame.grid_columnconfigure((0,1,2), weight=1)
        # Income card
        income_card = tk.Frame(summary_frame, bg=COLORS['GREEN'], relief='solid', bd=1)
        income_card.grid(row=0, column=0, sticky='ew', padx=(0,10), pady=5)
        tk.Label(income_card, text="Total Income", font=FONTS['FORM_LABEL'], 
                fg=COLORS['BLACK'], bg=COLORS['GREEN']).pack(pady=(10,5))
        tk.Label(income_card, text=f"{total_income:.2f} BDT", font=FONTS['VALUE'], 
                fg=COLORS['BLACK'], bg=COLORS['GREEN']).pack(pady=(0,10))
        # Expenses card
        expense_card = tk.Frame(summary_frame, bg=COLORS['GREY'], relief='solid', bd=1)
        expense_card.grid(row=0, column=1, sticky='ew', padx=5, pady=5)
        tk.Label(expense_card, text="Total Expenses", font=FONTS['FORM_LABEL'], 
                fg=COLORS['BLACK'], bg=COLORS['GREY']).pack(pady=(10,5))
        tk.Label(expense_card, text=f"{total_expenses:.2f} BDT", font=FONTS['VALUE'], 
                fg=COLORS['BLACK'], bg=COLORS['GREY']).pack(pady=(0,10))
        # Net cashflow card
        cashflow_color = COLORS['GREEN'] if net_cashflow >= 0 else COLORS['RED']
        cashflow_card = tk.Frame(summary_frame, bg=cashflow_color, relief='solid', bd=1)
        cashflow_card.grid(row=0, column=2, sticky='ew', padx=(10,0), pady=5)
        tk.Label(cashflow_card, text="Net Cashflow", font=FONTS['FORM_LABEL'], 
                fg=COLORS['WHITE'] if net_cashflow < 0 else COLORS['BLACK'], bg=cashflow_color).pack(pady=(10,5))
        tk.Label(cashflow_card, text=f"{net_cashflow:.2f} BDT", font=FONTS['VALUE'], 
                fg=COLORS['WHITE'] if net_cashflow < 0 else COLORS['BLACK'], bg=cashflow_color).pack(pady=(0,10))
        # Add chart
        self._create_trend_chart(parent_frame, report_data, "Income vs Expenses Trend")
        # Recent transactions
        self._create_recent_transactions_section(parent_frame, report_data)
    def _create_category_analysis_preview(self, parent_frame, report_data):
        """Create category analysis report preview"""
        tk.Label(parent_frame, text="Category Breakdown", font=FONTS['FORM_HEADER'], 
                fg=COLORS['BLACK'], bg=COLORS['WHITE']).pack(anchor='w', padx=20, pady=(0,15))
        # Calculate category totals
        category_totals = {}
        for transaction in report_data['transactions']:
            if transaction['CategoryName'] and transaction['TransactionType'] in ['Income', 'Expense']:
                category = transaction['CategoryName']
                amount = float(transaction['Amount'])
                trans_type = transaction['TransactionType']
                if category not in category_totals:
                    category_totals[category] = {'Income': 0, 'Expense': 0}
                category_totals[category][trans_type] += amount
        if category_totals:
            # Create category table
            table_frame = tk.Frame(parent_frame, bg=COLORS['WHITE'])
            table_frame.pack(fill='x', padx=20, pady=(0,20))
            # Headers
            header_frame = tk.Frame(table_frame, bg=COLORS['GREY'], relief='solid', bd=1)
            header_frame.pack(fill='x', pady=(0,1))
            tk.Label(header_frame, text="Category", font=FONTS['FORM_LABEL'], 
                    fg=COLORS['BLACK'], bg=COLORS['GREY']).pack(side='left', padx=10, pady=8)
            tk.Label(header_frame, text="Income", font=FONTS['FORM_LABEL'], 
                    fg=COLORS['BLACK'], bg=COLORS['GREY']).pack(side='right', padx=10, pady=8)
            tk.Label(header_frame, text="Expenses", font=FONTS['FORM_LABEL'], 
                    fg=COLORS['BLACK'], bg=COLORS['GREY']).pack(side='right', padx=10, pady=8)
            tk.Label(header_frame, text="Net", font=FONTS['FORM_LABEL'], 
                    fg=COLORS['BLACK'], bg=COLORS['GREY']).pack(side='right', padx=10, pady=8)
            # Category rows
            for category, amounts in category_totals.items():
                net = amounts['Income'] - amounts['Expense']
                row_frame = tk.Frame(table_frame, bg=COLORS['WHITE'], relief='solid', bd=1)
                row_frame.pack(fill='x', pady=1)
                tk.Label(row_frame, text=category, font=FONTS['LIST_ITEM'], 
                        fg=COLORS['BLACK'], bg=COLORS['WHITE']).pack(side='left', padx=10, pady=5)
                net_color = COLORS['GREEN'] if net >= 0 else COLORS['RED']
                tk.Label(row_frame, text=f"{net:.2f}", font=FONTS['LIST_ITEM'], 
                        fg=net_color, bg=COLORS['WHITE']).pack(side='right', padx=10, pady=5)
                tk.Label(row_frame, text=f"{amounts['Expense']:.2f}", font=FONTS['LIST_ITEM'], 
                        fg=COLORS['BLACK'], bg=COLORS['WHITE']).pack(side='right', padx=10, pady=5)
                tk.Label(row_frame, text=f"{amounts['Income']:.2f}", font=FONTS['LIST_ITEM'], 
                        fg=COLORS['BLACK'], bg=COLORS['WHITE']).pack(side='right', padx=10, pady=5)
        # Add pie chart for expenses
        self._create_expense_pie_chart(parent_frame, report_data)
    def _create_account_performance_preview(self, parent_frame, report_data):
        """Create account performance report preview"""
        tk.Label(parent_frame, text="Account Performance", font=FONTS['FORM_HEADER'], 
                fg=COLORS['BLACK'], bg=COLORS['WHITE']).pack(anchor='w', padx=20, pady=(0,15))
        # Account summary table
        table_frame = tk.Frame(parent_frame, bg=COLORS['WHITE'])
        table_frame.pack(fill='x', padx=20, pady=(0,20))
        # Headers
        header_frame = tk.Frame(table_frame, bg=COLORS['GREY'], relief='solid', bd=1)
        header_frame.pack(fill='x', pady=(0,1))
        tk.Label(header_frame, text="Account", font=FONTS['FORM_LABEL'], 
                fg=COLORS['BLACK'], bg=COLORS['GREY']).pack(side='left', padx=10, pady=8)
        tk.Label(header_frame, text="Type", font=FONTS['FORM_LABEL'], 
                fg=COLORS['BLACK'], bg=COLORS['GREY']).pack(side='left', padx=50, pady=8)
        tk.Label(header_frame, text="Current Balance", font=FONTS['FORM_LABEL'], 
                fg=COLORS['BLACK'], bg=COLORS['GREY']).pack(side='right', padx=10, pady=8)
        # Account rows
        for account_id, account_info in report_data['accounts'].items():
            row_frame = tk.Frame(table_frame, bg=COLORS['WHITE'], relief='solid', bd=1)
            row_frame.pack(fill='x', pady=1)
            tk.Label(row_frame, text=account_info['name'], font=FONTS['LIST_ITEM'], 
                    fg=COLORS['BLACK'], bg=COLORS['WHITE']).pack(side='left', padx=10, pady=5)
            tk.Label(row_frame, text=account_info['type'], font=FONTS['LIST_ITEM'], 
                    fg=COLORS['BLACK'], bg=COLORS['WHITE']).pack(side='left', padx=50, pady=5)
            balance_color = COLORS['GREEN'] if account_info['balance'] >= 0 else COLORS['RED']
            tk.Label(row_frame, text=f"{account_info['balance']:.2f} BDT", font=FONTS['LIST_ITEM'], 
                    fg=balance_color, bg=COLORS['WHITE']).pack(side='right', padx=10, pady=5)
        # Account activity chart
        self._create_account_activity_chart(parent_frame, report_data)
    def _create_budget_analysis_preview(self, parent_frame, report_data):
        """Create budget analysis report preview"""
        tk.Label(parent_frame, text="Budget vs Actual Spending", font=FONTS['FORM_HEADER'], 
                fg=COLORS['BLACK'], bg=COLORS['WHITE']).pack(anchor='w', padx=20, pady=(0,15))
        if report_data['budgets']:
            for budget in report_data['budgets']:
                budget_frame = tk.Frame(parent_frame, bg=COLORS['WHITE'], relief='solid', bd=1)
                budget_frame.pack(fill='x', padx=20, pady=5)
                # Budget header
                header_frame = tk.Frame(budget_frame, bg=COLORS['LIGHT_GREY'])
                header_frame.pack(fill='x', padx=5, pady=5)
                tk.Label(header_frame, text=f"{budget['category_name']} Budget", 
                        font=FONTS['FORM_LABEL'], fg=COLORS['BLACK'], bg=COLORS['LIGHT_GREY']).pack(side='left', padx=10)
                tk.Label(header_frame, text=f"{budget['time_period']}", 
                        font=FONTS['FORM_LABEL'], fg=COLORS['GREY'], bg=COLORS['LIGHT_GREY']).pack(side='right', padx=10)
                # Budget details
                details_frame = tk.Frame(budget_frame, bg=COLORS['WHITE'])
                details_frame.pack(fill='x', padx=15, pady=10)
                tk.Label(details_frame, text=f"Budget: {budget['budget_amount']:.2f} BDT", 
                        font=FONTS['LIST_ITEM'], fg=COLORS['BLACK'], bg=COLORS['WHITE']).pack(anchor='w')
                tk.Label(details_frame, text=f"Spent: {budget['spent_amount']:.2f} BDT", 
                        font=FONTS['LIST_ITEM'], fg=COLORS['BLACK'], bg=COLORS['WHITE']).pack(anchor='w')
                tk.Label(details_frame, text=f"Remaining: {budget['remaining_amount']:.2f} BDT", 
                        font=FONTS['LIST_ITEM'], fg=COLORS['GREEN'] if budget['remaining_amount'] > 0 else COLORS['RED'], 
                        bg=COLORS['WHITE']).pack(anchor='w')
                # Progress bar
                progress_frame = tk.Frame(details_frame, bg=COLORS['LIGHT_GREY'], height=20, relief='solid', bd=1)
                progress_frame.pack(fill='x', pady=(10,0))
                progress_frame.pack_propagate(False)
                if budget['budget_amount'] > 0:
                    spent_percentage = min(budget['spent_amount'] / budget['budget_amount'], 1.0)
                    progress_color = COLORS['RED'] if spent_percentage > 0.8 else COLORS['YELLOW'] if spent_percentage > 0.6 else COLORS['GREEN']
                    progress_fill = tk.Frame(progress_frame, bg=progress_color, height=20)
                    progress_fill.place(relwidth=spent_percentage, relheight=1)
                    tk.Label(progress_frame, text=f"{spent_percentage*100:.1f}%", 
                            font=('inter', 9, 'bold'), fg=COLORS['BLACK'], bg=COLORS['LIGHT_GREY']).place(relx=0.5, rely=0.5, anchor='center')
        else:
            tk.Label(parent_frame, text="No budgets found for this period", 
                    font=FONTS['LIST_ITEM'], fg=COLORS['GREY'], bg=COLORS['WHITE']).pack(anchor='w', padx=20, pady=10)
    def _create_complete_financial_preview(self, parent_frame, report_data):
        """Create complete financial report preview"""
        # Summary section
        self._create_monthly_summary_preview(parent_frame, report_data)
        # Category section
        self._create_category_analysis_preview(parent_frame, report_data)
        # Account section
        self._create_account_performance_preview(parent_frame, report_data)
        # Budget section
        self._create_budget_analysis_preview(parent_frame, report_data)
        # Savings goals section
        if report_data['saving_goals']:
            self._create_savings_goals_progress(parent_frame, report_data['saving_goals'])
    def _create_trend_chart(self, parent_frame, report_data, title):
        """Create trend chart for transactions"""
        try:
            chart_frame = tk.Frame(parent_frame, bg=COLORS['WHITE'])
            chart_frame.pack(fill='x', padx=20, pady=10)
            tk.Label(chart_frame, text=title, font=FONTS['FORM_HEADER'], 
                    fg=COLORS['BLACK'], bg=COLORS['WHITE']).pack(anchor='w', pady=(0,10))
            fig = Figure(figsize=(8, 4), dpi=80, facecolor='white')
            ax = fig.add_subplot(111)
            # Group transactions by date
            daily_data = {}
            for transaction in report_data['transactions']:
                date_str = transaction['Date_Created'][:10]  # Get date part
                amount = float(transaction['Amount'])
                trans_type = transaction['TransactionType']
                if date_str not in daily_data:
                    daily_data[date_str] = {'Income': 0, 'Expense': 0}
                if trans_type in ['Income', 'Expense']:
                    daily_data[date_str][trans_type] += amount
            if daily_data:
                dates = sorted(daily_data.keys())
                incomes = [daily_data[date]['Income'] for date in dates]
                expenses = [daily_data[date]['Expense'] for date in dates]
                # Convert dates for plotting
                date_objects = [datetime.strptime(date, '%Y-%m-%d') for date in dates]
                ax.plot(date_objects, incomes, label='Income', color='green', marker='o')
                ax.plot(date_objects, expenses, label='Expenses', color='red', marker='s')
                ax.set_title(title)
                ax.set_ylabel('Amount (BDT)')
                ax.legend()
                ax.grid(True, alpha=0.3)
                # Format x-axis
                ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
                fig.autofmt_xdate()
            else:
                ax.text(0.5, 0.5, 'No data available for chart', ha='center', va='center', transform=ax.transAxes)
                ax.set_title(title)
            # Embed chart in tkinter
            canvas = FigureCanvasTkAgg(fig, chart_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill='both', expand=True)
        except Exception as e:
            # Show error message
            error_label = tk.Label(chart_frame, text="Chart preview unavailable", 
                                  font=FONTS['LIST_ITEM'], fg=COLORS['GREY'], bg=COLORS['WHITE'])
            error_label.pack(pady=20)
    def _create_expense_pie_chart(self, parent_frame, report_data):
        """Create pie chart for expense categories"""
        try:
            chart_frame = tk.Frame(parent_frame, bg=COLORS['WHITE'])
            chart_frame.pack(fill='x', padx=20, pady=10)
            tk.Label(chart_frame, text="Expense Distribution", font=FONTS['FORM_HEADER'], 
                    fg=COLORS['BLACK'], bg=COLORS['WHITE']).pack(anchor='w', pady=(0,10))
            fig = Figure(figsize=(6, 6), dpi=80, facecolor='white')
            ax = fig.add_subplot(111)
            # Calculate expense categories
            category_expenses = {}
            for transaction in report_data['transactions']:
                if transaction['TransactionType'] == 'Expense' and transaction['CategoryName']:
                    category = transaction['CategoryName']
                    amount = float(transaction['Amount'])
                    category_expenses[category] = category_expenses.get(category, 0) + amount
            if category_expenses:
                categories = list(category_expenses.keys())
                amounts = list(category_expenses.values())
                ax.pie(amounts, labels=categories, autopct='%1.1f%%', startangle=90)
                ax.set_title('Expenses by Category')
            else:
                ax.text(0.5, 0.5, 'No expense data available', ha='center', va='center', transform=ax.transAxes)
                ax.set_title('Expenses by Category')
            # Embed chart in tkinter
            canvas = FigureCanvasTkAgg(fig, chart_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill='both', expand=True)
        except Exception as e:
            # Show error message
            error_label = tk.Label(chart_frame, text="Chart preview unavailable", 
                                  font=FONTS['LIST_ITEM'], fg=COLORS['GREY'], bg=COLORS['WHITE'])
            error_label.pack(pady=20)
    def _create_account_activity_chart(self, parent_frame, report_data):
        """Create account activity chart"""
        try:
            chart_frame = tk.Frame(parent_frame, bg=COLORS['WHITE'])
            chart_frame.pack(fill='x', padx=20, pady=10)
            tk.Label(chart_frame, text="Account Activity", font=FONTS['FORM_HEADER'], 
                    fg=COLORS['BLACK'], bg=COLORS['WHITE']).pack(anchor='w', pady=(0,10))
            fig = Figure(figsize=(8, 4), dpi=80, facecolor='white')
            ax = fig.add_subplot(111)
            # Calculate account activity
            account_activity = {}
            for transaction in report_data['transactions']:
                account_name = transaction['AccountName']
                amount = float(transaction['Amount'])
                if account_name not in account_activity:
                    account_activity[account_name] = 0
                account_activity[account_name] += amount
            if account_activity:
                accounts = list(account_activity.keys())
                activity = list(account_activity.values())
                bars = ax.bar(accounts, activity, color=['green' if a > 0 else 'red' for a in activity], alpha=0.7)
                ax.set_title('Transaction Volume by Account')
                ax.set_ylabel('Total Transaction Amount (BDT)')
                # Add value labels on bars
                for bar, amount in zip(bars, activity):
                    height = bar.get_height()
                    ax.text(bar.get_x() + bar.get_width()/2., height,
                           f'{amount:.0f}', ha='center', va='bottom')
                # Rotate x-axis labels if needed
                plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
            else:
                ax.text(0.5, 0.5, 'No account activity data', ha='center', va='center', transform=ax.transAxes)
                ax.set_title('Transaction Volume by Account')
            # Embed chart in tkinter
            canvas = FigureCanvasTkAgg(fig, chart_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill='both', expand=True)
        except Exception as e:
            # Show error message
            error_label = tk.Label(chart_frame, text="Chart preview unavailable", 
                                  font=FONTS['LIST_ITEM'], fg=COLORS['GREY'], bg=COLORS['WHITE'])
            error_label.pack(pady=20)
    def _create_recent_transactions_section(self, parent_frame, report_data):
        """Create recent transactions section"""
        tk.Label(parent_frame, text="Recent Transactions", font=FONTS['FORM_HEADER'], 
                fg=COLORS['BLACK'], bg=COLORS['WHITE']).pack(anchor='w', padx=20, pady=(20,10))
        recent_transactions = report_data['transactions'][:10]  # Show last 10
        if recent_transactions:
            for transaction in recent_transactions:
                trans_frame = tk.Frame(parent_frame, bg=COLORS['LIGHT_GREY'], relief='solid', bd=1)
                trans_frame.pack(fill='x', padx=20, pady=2)
                # Transaction details
                details_frame = tk.Frame(trans_frame, bg=COLORS['LIGHT_GREY'])
                details_frame.pack(fill='x', padx=10, pady=5)
                # Left side - description and account
                left_text = f"{transaction['Description'] or 'No description'}\n{transaction['AccountName']}"
                if transaction['CategoryName']:
                    left_text += f" • {transaction['CategoryName']}"
                tk.Label(details_frame, text=left_text, font=FONTS['LIST_ITEM'], 
                        fg=COLORS['BLACK'], bg=COLORS['LIGHT_GREY'], anchor='w', justify='left').pack(side='left')
                # Right side - amount and date
                amount = float(transaction['Amount'])
                prefix = "+" if transaction['TransactionType'] == 'Income' else "-" if transaction['TransactionType'] == 'Expense' else "→"
                amount_color = COLORS['GREEN'] if transaction['TransactionType'] == 'Income' else COLORS['RED'] if transaction['TransactionType'] == 'Expense' else COLORS['BLUE']
                date_str = transaction['Date_Created'][:10]
                right_text = f"{prefix}{amount:.2f} BDT\n{date_str}"
                tk.Label(details_frame, text=right_text, font=FONTS['LIST_ITEM'], 
                        fg=amount_color, bg=COLORS['LIGHT_GREY'], anchor='e', justify='right').pack(side='right')
        else:
            tk.Label(parent_frame, text="No transactions found for this period", 
                    font=FONTS['LIST_ITEM'], fg=COLORS['GREY'], bg=COLORS['WHITE']).pack(anchor='w', padx=20, pady=10)
    def _create_savings_goals_progress(self, parent_frame, saving_goals):
        """Create savings goals progress section"""
        tk.Label(parent_frame, text="Savings Goals Progress", font=FONTS['FORM_HEADER'], 
                fg=COLORS['BLACK'], bg=COLORS['WHITE']).pack(anchor='w', padx=20, pady=(20,10))
        for goal in saving_goals:
            if not goal.is_default:  # Skip default goals
                progress = goal.progress_percentage()
                goal_frame = tk.Frame(parent_frame, bg=COLORS['WHITE'])
                goal_frame.pack(fill='x', padx=20, pady=5)
                tk.Label(goal_frame, text=f"{goal.goal_name}: {goal.current_amount:.2f} / {goal.target_amount:.2f} BDT ({progress:.1f}%)", 
                        font=FONTS['LIST_ITEM'], fg=COLORS['BLACK'], bg=COLORS['WHITE']).pack(anchor='w')
                # Progress bar
                progress_frame = tk.Frame(goal_frame, bg=COLORS['LIGHT_GREY'], height=15, relief='solid', bd=1)
                progress_frame.pack(fill='x', pady=(5,0))
                progress_frame.pack_propagate(False)
                progress_fill = tk.Frame(progress_frame, bg=COLORS['GREEN'], height=15)
                progress_fill.place(relwidth=min(progress/100, 1.0), relheight=1)
# =============================================================================
# APPLICATION CONTROLLER
# =============================================================================
class FinanceApp:
    """Main application controller"""
    def __init__(self):
        # Don't create main window yet - start with login popup
        self.main_root = None
        self.login_window = None
        self.database = None
        self.current_user = None
        self.current_screen = None
        # Initialize database first
        try:
            self.database = Database()
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to initialize database: {e}")
            sys.exit(1)
        # Start with login popup
        self.show_login_popup()
    def show_login_popup(self):
        """Show compact login popup window"""
        try:
            # Create small popup window for login
            self.login_window = tk.Tk()
            self.login_window.title("Finance Manager - Login")
            self.login_window.geometry("400x450")
            self.login_window.resizable(False, False)
            # Center the window on screen
            self.login_window.update_idletasks()
            width = self.login_window.winfo_width()
            height = self.login_window.winfo_height()
            x = (self.login_window.winfo_screenwidth() // 2) - (width // 2)
            y = (self.login_window.winfo_screenheight() // 2) - (height // 2)
            self.login_window.geometry(f"{width}x{height}+{x}+{y}")
            # Window icon removed per user request
            # Set up window close handler
            self.login_window.protocol("WM_DELETE_WINDOW", self.on_login_closing)
            self.current_screen = LoginScreen(
                parent=self.login_window,
                database=self.database,
                on_login_success=self.on_login_success,
                on_show_register=self.show_register_popup
            )
        except Exception as e:
            messagebox.showerror("Error", f"Failed to show login screen: {e}")
    def show_register_popup(self):
        """Show compact registration popup window"""
        try:
            # Clear current window
            for widget in self.login_window.winfo_children():
                widget.destroy()
            # Resize window for registration (taller to accommodate more fields)
            self.login_window.geometry("400x520")
            # Center the window on screen after resize
            self.login_window.update_idletasks()
            width = self.login_window.winfo_width()
            height = self.login_window.winfo_height()
            x = (self.login_window.winfo_screenwidth() // 2) - (width // 2)
            y = (self.login_window.winfo_screenheight() // 2) - (height // 2)
            self.login_window.geometry(f"{width}x{height}+{x}+{y}")
            self.login_window.title("Finance Manager - Register")
            self.current_screen = RegisterScreen(
                parent=self.login_window,
                database=self.database,
                on_register_success=self.on_register_success,
                on_show_login=self.show_login_popup_content
            )
        except Exception as e:
            messagebox.showerror("Error", f"Failed to show register screen: {e}")
    def show_login_popup_content(self):
        """Show login content in existing popup window"""
        try:
            # Clear current window
            for widget in self.login_window.winfo_children():
                widget.destroy()
            # Resize back to login size (smaller)
            self.login_window.geometry("400x450")
            # Center the window on screen after resize
            self.login_window.update_idletasks()
            width = self.login_window.winfo_width()
            height = self.login_window.winfo_height()
            x = (self.login_window.winfo_screenwidth() // 2) - (width // 2)
            y = (self.login_window.winfo_screenheight() // 2) - (height // 2)
            self.login_window.geometry(f"{width}x{height}+{x}+{y}")
            self.login_window.title("Finance Manager - Login")
            self.current_screen = LoginScreen(
                parent=self.login_window,
                database=self.database,
                on_login_success=self.on_login_success,
                on_show_register=self.show_register_popup
            )
        except Exception as e:
            messagebox.showerror("Error", f"Failed to show login screen: {e}")
    def on_register_success(self):
        """Handle successful registration"""
        messagebox.showinfo("Success", "Registration successful! Please login.")
        self.show_login_popup_content()
    def on_login_success(self, user):
        """Handle successful login"""
        try:
            self.current_user = user
            # Close login popup
            self.login_window.destroy()
            self.login_window = None
            # Create main application window
            self.create_main_window()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load main application: {e}")
    def create_main_window(self):
        """Create the main application window after successful login"""
        try:
            # Create main window
            self.main_root = tk.Tk()
            self.main_root.title(WINDOW_TITLE)
            self.main_root.geometry(WINDOW_SIZE)
            self.main_root.resizable(True, True)
            # Set up window close handler
            self.main_root.protocol("WM_DELETE_WINDOW", self.on_closing)
            # Show main application
            self.show_main_app()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create main window: {e}")
    def show_main_app(self):
        """Show the main application"""
        try:
            self.current_screen = MainApp(
                parent=self.main_root,
                database=self.database,
                user=self.current_user,
                on_logout=self.on_logout
            )
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load main application: {e}")
    def on_logout(self):
        """Handle user logout"""
        try:
            self.current_user = None
            # Close main window
            if self.main_root:
                self.main_root.destroy()
                self.main_root = None
            # Show login popup again
            self.show_login_popup()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to logout: {e}")
    def on_login_closing(self):
        """Handle login window closing"""
        try:
            self.cleanup_and_exit()
        except Exception as e:
            pass
        finally:
            sys.exit(0)
    def on_closing(self):
        """Handle main application closing"""
        try:
            if self.current_user:
                pass
            self.cleanup_and_exit()
        except Exception as e:
            pass
        finally:
            sys.exit(0)
    def cleanup_and_exit(self):
        """Cleanup resources and exit"""
        # Close database connection
        if hasattr(self.database, 'close') and self.database:
            self.database.close()
        # Destroy windows
        if self.main_root:
            self.main_root.destroy()
        if self.login_window:
            self.login_window.destroy()
    def run(self):
        """Start the application"""
        try:
            if self.login_window:
                self.login_window.mainloop()
        except KeyboardInterrupt:
            self.cleanup_and_exit()
        except Exception as e:
            messagebox.showerror("Fatal Error", f"An unexpected error occurred: {e}")
            sys.exit(1)
# =============================================================================
# MAIN ENTRY POINT
# =============================================================================
def main():
    """Main entry point"""
    try:
        app = FinanceApp()
        app.run()
    except Exception as e:
        if tk._default_root:
            messagebox.showerror("Fatal Error", f"Failed to start application: {e}")
        sys.exit(1)
if __name__ == "__main__":
    main() 
