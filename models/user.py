"""
User model for Finance Management Application
"""

from typing import Optional, Dict, Any
from datetime import datetime
import re
from config import VALIDATION
from .exceptions import ValidationError


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