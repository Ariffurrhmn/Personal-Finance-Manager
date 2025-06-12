"""
Category model for Finance Management Application
"""

from typing import Optional, Dict, Any
from config import VALIDATION
from .exceptions import ValidationError


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