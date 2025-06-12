"""
Transaction model for Finance Management Application
"""

from typing import Optional, Dict, Any
from datetime import datetime
from config import VALIDATION
from .exceptions import ValidationError


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