"""
Account model for Finance Management Application
"""

from typing import Optional, Dict, Any
from config import VALIDATION
from .exceptions import ValidationError


class Account:
    """Account model with validation"""
    
    VALID_TYPES = ["Bank", "Cash", "Savings"]
    
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