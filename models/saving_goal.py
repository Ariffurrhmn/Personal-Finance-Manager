"""
SavingGoal model for Finance Management Application
"""

from typing import Optional, Dict, Any
from datetime import datetime
from config import VALIDATION
from .exceptions import ValidationError


class SavingGoal:
    """Saving goal model with validation"""
    
    def __init__(self, goal_id: Optional[int] = None, user_id: int = 0,
                 goal_name: str = "", target_amount: float = 0.0,
                 current_amount: float = 0.0, account_id: Optional[int] = None,
                 is_default: bool = False, date_created: Optional[str] = None):
        self.goal_id = goal_id
        self.user_id = user_id
        self.goal_name = goal_name
        self.target_amount = target_amount
        self.current_amount = current_amount
        self.account_id = account_id
        self.is_default = is_default
        self.date_created = date_created or datetime.now().isoformat()
    
    def validate(self) -> None:
        """Validate saving goal data"""
        if not self.goal_name or len(self.goal_name.strip()) == 0:
            raise ValidationError("Goal name is required")
        
        if len(self.goal_name) > VALIDATION['MAX_NAME_LENGTH']:
            raise ValidationError(f"Goal name must be less than {VALIDATION['MAX_NAME_LENGTH']} characters")
        
        if self.target_amount < 0:
            raise ValidationError("Target amount cannot be negative")
        
        if self.current_amount < 0:
            raise ValidationError("Current amount cannot be negative")
        
        if self.user_id <= 0:
            raise ValidationError("Invalid user ID")
    
    def is_completed(self) -> bool:
        """Check if goal is completed"""
        return self.current_amount >= self.target_amount and self.target_amount > 0
    
    def progress_percentage(self) -> float:
        """Get progress percentage"""
        if self.target_amount <= 0:
            return 0.0
        return min((self.current_amount / self.target_amount) * 100, 100.0)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'goal_id': self.goal_id,
            'user_id': self.user_id,
            'goal_name': self.goal_name,
            'target_amount': self.target_amount,
            'current_amount': self.current_amount,
            'account_id': self.account_id,
            'is_default': self.is_default,
            'date_created': self.date_created
        } 