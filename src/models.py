"""
Data models for the Finance Management Application
"""

from datetime import datetime
from typing import Optional, Dict, Any
import re
try:
    from .config import VALIDATION
except ImportError:
    from config import VALIDATION

class ValidationError(Exception):
    """Custom exception for validation errors"""
    pass

class User:
    """User model with validation"""
    
    def __init__(self, user_id: Optional[int] = None, name: str = "", 
                 email: str = "", password: str = "", date_joined: Optional[str] = None):
        self.user_id = user_id
        self.name = name
        self.email = email
        self.password = password
        self.date_joined = date_joined or datetime.now().isoformat()
    
    def validate(self) -> None:
        """Validate user data"""
        if not self.name or len(self.name.strip()) == 0:
            raise ValidationError("Name is required")
        
        if len(self.name) > VALIDATION['MAX_NAME_LENGTH']:
            raise ValidationError(f"Name must be less than {VALIDATION['MAX_NAME_LENGTH']} characters")
        
        if not self.email or len(self.email.strip()) == 0:
            raise ValidationError("Email is required")
        
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, self.email):
            raise ValidationError("Invalid email format")
        
        if not self.password or len(self.password) < 6:
            raise ValidationError("Password must be at least 6 characters")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'user_id': self.user_id,
            'name': self.name,
            'email': self.email,
            'password': self.password,
            'date_joined': self.date_joined
        }

class Account:
    """Account model with validation"""
    
    VALID_TYPES = ["Bank", "Cash", "Internet Bank"]
    
    def __init__(self, account_id: Optional[int] = None, user_id: int = 0,
                 name: str = "", balance: float = 0.0, account_type: str = "Bank"):
        self.account_id = account_id
        self.user_id = user_id
        self.name = name
        self.balance = balance
        self.account_type = account_type
    
    def validate(self) -> None:
        """Validate account data"""
        if not self.name or len(self.name.strip()) == 0:
            raise ValidationError("Account name is required")
        
        if len(self.name) > VALIDATION['MAX_NAME_LENGTH']:
            raise ValidationError(f"Account name must be less than {VALIDATION['MAX_NAME_LENGTH']} characters")
        
        if self.account_type not in self.VALID_TYPES:
            raise ValidationError(f"Account type must be one of: {', '.join(self.VALID_TYPES)}")
        
        if self.balance < 0:
            raise ValidationError("Account balance cannot be negative")
        
        if self.user_id <= 0:
            raise ValidationError("Invalid user ID")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'account_id': self.account_id,
            'user_id': self.user_id,
            'name': self.name,
            'balance': self.balance,
            'account_type': self.account_type
        }

class Category:
    """Category model with validation"""
    
    VALID_TYPES = ["Income", "Expense"]
    
    def __init__(self, category_id: Optional[int] = None, user_id: int = 0,
                 name: str = "", category_type: str = "Expense"):
        self.category_id = category_id
        self.user_id = user_id
        self.name = name
        self.category_type = category_type
    
    def validate(self) -> None:
        """Validate category data"""
        if not self.name or len(self.name.strip()) == 0:
            raise ValidationError("Category name is required")
        
        if len(self.name) > VALIDATION['MAX_NAME_LENGTH']:
            raise ValidationError(f"Category name must be less than {VALIDATION['MAX_NAME_LENGTH']} characters")
        
        if self.category_type not in self.VALID_TYPES:
            raise ValidationError(f"Category type must be one of: {', '.join(self.VALID_TYPES)}")
        
        if self.user_id <= 0:
            raise ValidationError("Invalid user ID")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'category_id': self.category_id,
            'user_id': self.user_id,
            'name': self.name,
            'category_type': self.category_type
        }

class Transaction:
    """Transaction model with validation"""
    
    VALID_TYPES = ["Income", "Expense", "Transfer"]
    
    def __init__(self, transaction_id: Optional[int] = None, user_id: int = 0,
                 account_id: int = 0, category_id: Optional[int] = None,
                 amount: float = 0.0, description: str = "", 
                 transaction_type: str = "Expense", 
                 to_account_id: Optional[int] = None,
                 date_created: Optional[str] = None):
        self.transaction_id = transaction_id
        self.user_id = user_id
        self.account_id = account_id
        self.category_id = category_id
        self.amount = amount
        self.description = description
        self.transaction_type = transaction_type
        self.to_account_id = to_account_id
        self.date_created = date_created or datetime.now().isoformat()
    
    def validate(self) -> None:
        """Validate transaction data"""
        if self.amount <= 0:
            raise ValidationError("Transaction amount must be positive")
        
        if self.amount > VALIDATION['MAX_AMOUNT']:
            raise ValidationError(f"Transaction amount cannot exceed {VALIDATION['MAX_AMOUNT']}")
        
        if self.transaction_type not in self.VALID_TYPES:
            raise ValidationError(f"Transaction type must be one of: {', '.join(self.VALID_TYPES)}")
        
        if self.user_id <= 0:
            raise ValidationError("Invalid user ID")
        
        if self.account_id <= 0:
            raise ValidationError("Invalid account ID")
        
        if self.transaction_type in ["Income", "Expense"] and not self.category_id:
            raise ValidationError("Category is required for income and expense transactions")
        
        if self.transaction_type == "Transfer" and not self.to_account_id:
            raise ValidationError("Destination account is required for transfers")
        
        if self.transaction_type == "Transfer" and self.account_id == self.to_account_id:
            raise ValidationError("Cannot transfer to the same account")
        
        if self.description and len(self.description) > VALIDATION['MAX_DESC_LENGTH']:
            raise ValidationError(f"Description must be less than {VALIDATION['MAX_DESC_LENGTH']} characters")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'transaction_id': self.transaction_id,
            'user_id': self.user_id,
            'account_id': self.account_id,
            'category_id': self.category_id,
            'amount': self.amount,
            'description': self.description,
            'transaction_type': self.transaction_type,
            'to_account_id': self.to_account_id,
            'date_created': self.date_created
        } 