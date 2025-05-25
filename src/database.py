"""
Database layer for the Finance Management Application
"""

import sqlite3
import hashlib
import secrets
from typing import List, Optional, Dict, Any, Tuple
from contextlib import contextmanager
import logging
try:
    from .config import DB_PATH, SALT_LENGTH, DEFAULT_ACCOUNTS, DEFAULT_CATEGORIES, SAVINGS_CONFIG, ACCOUNT_LIMITS
    from .models import User, Account, Category, Transaction, ValidationError
except ImportError:
    from config import DB_PATH, SALT_LENGTH, DEFAULT_ACCOUNTS, DEFAULT_CATEGORIES, SAVINGS_CONFIG, ACCOUNT_LIMITS
    from models import User, Account, Category, Transaction, ValidationError

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseError(Exception):
    """Custom exception for database errors"""
    pass

class Database:
    """Database management class with full CRUD operations"""
    
    def __init__(self, db_path: str = DB_PATH):
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
            # Don't convert ValidationError to DatabaseError
            if conn:
                conn.rollback()
            raise
        except sqlite3.IntegrityError:
            # Let IntegrityError pass through for specific handling
            if conn:
                conn.rollback()
            raise
        except sqlite3.Error as e:
            if conn:
                conn.rollback()
            logger.error(f"Database error: {e}")
            raise DatabaseError(f"Database operation failed: {e}")
        finally:
            if conn:
                conn.close()
    
    def init_database(self):
        """Initialize database with all required tables"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Create tables
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
                AccountType TEXT NOT NULL CHECK (AccountType IN ('Bank', 'Cash', 'Internet Bank')),
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
            """)
            
            conn.commit()
            logger.info("Database initialized successfully")
    
    def _hash_password(self, password: str, salt: str) -> str:
        """Hash password with salt"""
        return hashlib.sha256((password + salt).encode()).hexdigest()
    
    def _generate_salt(self) -> str:
        """Generate random salt"""
        return secrets.token_hex(SALT_LENGTH)
    
    # User operations
    def create_user(self, user: User) -> int:
        """Create a new user"""
        user.validate()
        
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
                logger.info(f"User created with ID: {user_id}")
                return user_id
                
        except sqlite3.IntegrityError as e:
            if "UNIQUE constraint failed: User.Email" in str(e):
                raise ValidationError("Email already exists")
            raise DatabaseError(f"Failed to create user: {e}")
        except DatabaseError:
            # Re-raise DatabaseError as is
            raise
    
    def _create_default_data(self, cursor, user_id: int):
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
    
    def authenticate_user(self, email: str, password: str) -> Optional[User]:
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
                            password="",  # Don't return password
                            date_joined=row['Date_Joined']
                        )
                return None
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return None
    
    def get_user(self, user_id: int) -> Optional[User]:
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
                    password="",  # Don't return password
                    date_joined=row['Date_Joined']
                )
            return None
    
    # Account operations
    def create_account(self, account: Account) -> int:
        """Create a new account"""
        account.validate()
        
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
            logger.info(f"Account created with ID: {account_id}")
            return account_id
    
    def get_user_accounts(self, user_id: int) -> List[Account]:
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
    
    def update_account(self, account: Account) -> bool:
        """Update an account"""
        account.validate()
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE Account SET Name = ?, Balance = ?, AccountType = ?
                WHERE AccountID = ? AND UserID = ?
            """, (account.name, account.balance, account.account_type, 
                  account.account_id, account.user_id))
            
            success = cursor.rowcount > 0
            conn.commit()
            return success
    
    def delete_account(self, account_id: int, user_id: int) -> bool:
        """Delete an account"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM Account WHERE AccountID = ? AND UserID = ?", 
                          (account_id, user_id))
            
            success = cursor.rowcount > 0
            conn.commit()
            return success
    
    def get_account(self, account_id: int, user_id: int) -> Optional[Account]:
        """Get account by ID"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Account WHERE AccountID = ? AND UserID = ?", 
                          (account_id, user_id))
            row = cursor.fetchone()
            
            if row:
                return Account(
                    account_id=row['AccountID'],
                    user_id=row['UserID'],
                    name=row['Name'],
                    balance=row['Balance'],
                    account_type=row['AccountType']
                )
            return None
    
    # Category operations
    def create_category(self, category: Category) -> int:
        """Create a new category"""
        category.validate()
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO Category (UserID, Name, CategoryType)
                VALUES (?, ?, ?)
            """, (category.user_id, category.name, category.category_type))
            
            category_id = cursor.lastrowid
            conn.commit()
            logger.info(f"Category created with ID: {category_id}")
            return category_id
    
    def get_user_categories(self, user_id: int) -> List[Category]:
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
    
    def delete_category(self, category_id: int, user_id: int) -> bool:
        """Delete a category"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM Category WHERE CategoryID = ? AND UserID = ?", 
                          (category_id, user_id))
            
            success = cursor.rowcount > 0
            conn.commit()
            return success
    
    # Transaction operations
    def create_transaction(self, transaction: Transaction) -> int:
        """Create a new transaction and update account balances"""
        transaction.validate()
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Start transaction
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
                    
                    # Basic balance check
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
                elif transaction.transaction_type == "Expense":
                    cursor.execute("UPDATE Account SET Balance = Balance - ? WHERE AccountID = ?",
                                 (transaction.amount, transaction.account_id))
                elif transaction.transaction_type == "Transfer":
                    cursor.execute("UPDATE Account SET Balance = Balance - ? WHERE AccountID = ?",
                                 (transaction.amount, transaction.account_id))
                    cursor.execute("UPDATE Account SET Balance = Balance + ? WHERE AccountID = ?",
                                 (transaction.amount, transaction.to_account_id))
                
                conn.commit()
                logger.info(f"Transaction created with ID: {transaction_id}")
                return transaction_id
                
            except Exception as e:
                conn.rollback()
                raise DatabaseError(f"Failed to create transaction: {e}")
    
    def get_user_transactions(self, user_id: int, limit: int = 50) -> List[Dict[str, Any]]:
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
    
    def get_user_balance_summary(self, user_id: int) -> Dict[str, float]:
        """Get balance summary for a user"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Total balance
            cursor.execute("SELECT SUM(Balance) as TotalBalance FROM Account WHERE UserID = ?", (user_id,))
            total_balance = cursor.fetchone()['TotalBalance'] or 0.0
            
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
                'monthly_income': monthly_income,
                'monthly_expense': monthly_expense,
                'monthly_cashflow': monthly_income - monthly_expense
            }
    
    def close(self):
        """Close database connection (for compatibility with tests)"""
        # SQLite connections are closed automatically when using context managers
        # This method is provided for compatibility with test tearDown methods
        pass 