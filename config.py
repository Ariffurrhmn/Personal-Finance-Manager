"""
Configuration module for Finance Management Application
Contains all constants, settings, and default values
"""

# Database configuration
DB_PATH = "finance_app.db"
DB_BACKUP_PATH = "finance_app_backup.db"

# UI Configuration
WINDOW_SIZE = "1024x768"
WINDOW_TITLE = "Finance Management"

# Asset paths - icons removed per user request

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

# Font configuration
FONTS = {
    'FAMILY': 'inter',
    'BALANCE': ('inter', 36, 'bold'),
    'HEADER': ('inter', 22, 'bold'),
    'SECTION_LABEL': ('inter', 13, 'italic'),
    'VALUE': ('inter', 16, 'bold'),
    'BUTTON': ('inter', 11, 'bold'),
    'TRANSACTION_DESC': ('inter', 12, 'bold'),
    'TRANSACTION_SUB': ('inter', 10, 'italic'),
    'TRANSACTION_AMOUNT': ('inter', 14, 'bold'),
    'TRANSACTION_DATE': ('inter', 9, 'normal'),
    'POPUP_AMOUNT': ('inter', 50, 'normal'),
    'POPUP_LABEL': ('inter', 10, 'italic'),
    'POPUP_SUBMIT': ('inter', 22, 'bold'),
    'LOGIN_TITLE': ('inter', 32, 'bold'),
    'LOGIN_INPUT': ('inter', 14, 'normal'),
    'LOGIN_BUTTON': ('inter', 16, 'bold'),
    'WELCOME': ('inter', 12, 'normal'),
    'LOGOUT': ('inter', 10, 'bold'),
    'LIST_ITEM': ('inter', 13, 'normal'),
    'FORM_LABEL': ('inter', 11, 'normal'),
    'FORM_HEADER': ('inter', 16, 'bold')
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