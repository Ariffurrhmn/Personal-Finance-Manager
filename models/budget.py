"""
Budget model for Finance Management Application
"""

from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from config import BUDGET_CONFIG, VALIDATION
from .exceptions import ValidationError


class Budget:
    """Budget model with validation"""
    
    VALID_TIME_PERIODS = BUDGET_CONFIG['TIME_PERIODS']
    
    def __init__(self, budget_id: Optional[int] = None, user_id: int = 0,
                 category_id: int = 0, budget_amount: float = 0.0,
                 time_period: str = "Month", start_date: Optional[str] = None,
                 end_date: Optional[str] = None, date_created: Optional[str] = None):
        self.budget_id = budget_id
        self.user_id = user_id
        self.category_id = category_id
        self.budget_amount = budget_amount
        self.time_period = time_period
        self.start_date = start_date or datetime.now().isoformat()
        self.end_date = end_date or self._calculate_end_date()
        self.date_created = date_created or datetime.now().isoformat()
    
    def _calculate_end_date(self) -> str:
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
    
    def validate(self) -> None:
        """Validate budget data"""
        if self.budget_amount <= 0:
            raise ValidationError("Budget amount must be positive")
        
        if self.budget_amount > VALIDATION['MAX_AMOUNT']:
            raise ValidationError(f"Budget amount cannot exceed {VALIDATION['MAX_AMOUNT']}")
        
        if self.time_period not in self.VALID_TIME_PERIODS:
            raise ValidationError(f"Time period must be one of: {', '.join(self.VALID_TIME_PERIODS)}")
        
        if self.user_id <= 0:
            raise ValidationError("Invalid user ID")
        
        if self.category_id <= 0:
            raise ValidationError("Invalid category ID")
    
    def is_expired(self) -> bool:
        """Check if budget period has expired"""
        return datetime.now() > datetime.fromisoformat(self.end_date.replace('Z', '+00:00'))
    
    def days_remaining(self) -> int:
        """Get days remaining in budget period"""
        end_date = datetime.fromisoformat(self.end_date.replace('Z', '+00:00'))
        remaining = (end_date - datetime.now()).days
        return max(0, remaining)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'budget_id': self.budget_id,
            'user_id': self.user_id,
            'category_id': self.category_id,
            'budget_amount': self.budget_amount,
            'time_period': self.time_period,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'date_created': self.date_created
        } 