"""
Database module for Finance Management Application
Contains database management classes and operations
"""

import sqlite3
import hashlib
import secrets
import logging
from typing import List, Optional, Dict, Any
from contextlib import contextmanager
from datetime import datetime

from config import (
    DB_PATH, SALT_LENGTH, DEFAULT_ACCOUNTS, DEFAULT_CATEGORIES, 
    DEFAULT_SAVING_GOAL, ACCOUNT_LIMITS, BUDGET_CONFIG
)
from models import (
    ValidationError, User, Account, Category, Transaction, 
    SavingGoal, Budget
)

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
            logger.error(f"Database error: {e}")
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
            logger.info("Database initialized successfully")
    
    def _migrate_account_table(self, cursor):
        """Migrate Account table to support new account types"""
        logger.info("Migrating Account table to support new account types")
        
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
        
        logger.info("Account table migration completed")
    
    def _hash_password(self, password: str, salt: str) -> str:
        """Hash password with salt"""
        return hashlib.sha256((password + salt).encode()).hexdigest()
    
    def _generate_salt(self) -> str:
        """Generate random salt"""
        return secrets.token_hex(SALT_LENGTH)
    
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
                            password="",
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
                    password="",
                    date_joined=row['Date_Joined']
                )
            return None
    
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
    
    def delete_account(self, account_id: int, user_id: int) -> bool:
        """Delete an account"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM Account WHERE AccountID = ? AND UserID = ?", 
                          (account_id, user_id))
            
            success = cursor.rowcount > 0
            conn.commit()
            return success
    
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
    
    def create_transaction(self, transaction: Transaction) -> int:
        """Create a new transaction and update account balances"""
        transaction.validate()
        
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
                logger.info(f"Transaction created with ID: {transaction_id}")
                return transaction_id
                
            except Exception as e:
                conn.rollback()
                raise DatabaseError(f"Failed to create transaction: {e}")
    
    def _update_saving_goal_from_account(self, cursor, account_id: int):
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
    
    def create_saving_goal(self, goal: SavingGoal) -> int:
        """Create a new saving goal and associated saving account"""
        goal.validate()
        
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
                logger.info(f"Saving goal created with ID: {goal_id}")
                return goal_id
                
            except Exception as e:
                conn.rollback()
                raise DatabaseError(f"Failed to create saving goal: {e}")
    
    def get_user_saving_goals(self, user_id: int) -> List[SavingGoal]:
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
    
    def update_saving_goal_amount(self, goal_id: int, new_amount: float) -> bool:
        """Update saving goal current amount"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE SavingGoal SET CurrentAmount = ? WHERE GoalID = ?
            """, (new_amount, goal_id))
            
            success = cursor.rowcount > 0
            conn.commit()
            return success
    
    def delete_saving_goal(self, goal_id: int, user_id: int) -> bool:
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
    
    def get_saving_accounts(self, user_id: int) -> List[Account]:
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
    
    def get_regular_accounts(self, user_id: int) -> List[Account]:
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
    
    def create_budget(self, budget: Budget) -> int:
        """Create a new budget"""
        budget.validate()
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO Budget (UserID, CategoryID, BudgetAmount, TimePeriod, StartDate, EndDate, Date_Created)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (budget.user_id, budget.category_id, budget.budget_amount, budget.time_period,
                  budget.start_date, budget.end_date, budget.date_created))
            
            budget_id = cursor.lastrowid
            conn.commit()
            logger.info(f"Budget created with ID: {budget_id}")
            return budget_id
    
    def get_user_budgets_with_spending(self, user_id: int) -> List[Dict[str, Any]]:
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
    
    def delete_budget(self, budget_id: int, user_id: int) -> bool:
        """Delete a budget"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM Budget WHERE BudgetID = ? AND UserID = ?", 
                          (budget_id, user_id))
            
            success = cursor.rowcount > 0
            conn.commit()
            return success
    
    def cleanup_expired_budgets(self, user_id: int) -> int:
        """Remove expired budgets and return count of removed budgets"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                DELETE FROM Budget WHERE UserID = ? AND datetime(EndDate) <= datetime('now')
            """, (user_id,))
            
            removed_count = cursor.rowcount
            conn.commit()
            return removed_count
    
    def check_budget_warning(self, user_id: int, category_id: int, amount: float) -> Optional[Dict[str, Any]]:
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

    def check_budget_exceeded(self, user_id: int, category_id: int, amount: float) -> Optional[Dict[str, Any]]:
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