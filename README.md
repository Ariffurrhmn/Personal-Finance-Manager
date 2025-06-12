# Finance Management Application

A comprehensive finance management application built with Python and Tkinter, featuring user management, transaction tracking, budgeting, and savings goals.

## Project Structure

The application has been refactored from a single monolithic file into a modular structure:

```
finance-app/
├── main.py                     # Main entry point
├── config.py                   # Configuration constants and settings
├── requirements.txt            # Python dependencies
├── Complete_app.py            # Original monolithic file (kept for compatibility)
├── models/                    # Data models
│   ├── __init__.py
│   ├── user.py               # User model
│   ├── account.py            # Account model
│   ├── category.py           # Category model
│   ├── transaction.py        # Transaction model
│   ├── saving_goal.py        # SavingGoal model
│   └── budget.py             # Budget model
├── database/                 # Database layer
│   ├── __init__.py
│   └── database.py           # Database management class
├── gui/                      # GUI components (placeholder structure)
│   ├── __init__.py
│   ├── auth/                 # Authentication screens
│   │   ├── __init__.py
│   │   ├── login_screen.py   # (To be extracted)
│   │   └── register_screen.py # (To be extracted)
│   └── popups/               # Popup dialogs
│       ├── __init__.py
│       ├── income_popup.py   # (To be extracted)
│       ├── expense_popup.py  # (To be extracted)
│       ├── transfer_popup.py # (To be extracted)
│       ├── saving_goal_popup.py # (To be extracted)
│       └── budget_popup.py   # (To be extracted)
└── (icons removed per user request)
```

## Features

- **User Authentication**: Secure login and registration system
- **Account Management**: Multiple account types (Bank, Cash, Savings)
- **Transaction Tracking**: Income, expenses, and transfers
- **Category Management**: Organize transactions by custom categories
- **Budgeting**: Set and monitor budgets with spending alerts
- **Savings Goals**: Track progress toward financial goals
- **Reporting**: Generate financial reports with charts
- **Data Persistence**: SQLite database for reliable data storage

## Installation

1. **Clone or download the project files**

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**:
   ```bash
   python main.py
   ```

## Configuration

All application settings are centralized in `config.py`:

- **Database settings**: Database file paths
- **UI configuration**: Window size, colors, fonts
- **Security settings**: Password requirements, salt length
- **Default data**: Initial accounts and categories for new users
- **Validation rules**: Amount limits, name length restrictions
- **Budget settings**: Warning thresholds, time periods

## Models

### Core Data Models

- **User**: User account with authentication
- **Account**: Financial accounts (Bank, Cash, Savings)
- **Category**: Transaction categories (Income/Expense)
- **Transaction**: Financial transactions with full validation
- **SavingGoal**: Savings targets with progress tracking
- **Budget**: Budget limits with spending monitoring

### Validation

All models include comprehensive validation:
- Required field validation
- Data type checking
- Business rule enforcement
- Amount and length limits

## Database

The application uses SQLite for data persistence with:

- **ACID compliance**: Reliable transaction processing
- **Foreign key constraints**: Data integrity
- **Automatic migration**: Seamless updates
- **Connection pooling**: Efficient resource usage
- **Logging**: Comprehensive operation tracking

### Database Schema

- `User`: User accounts with salted password hashing
- `Account`: Financial accounts with balance tracking
- `Category`: Transaction categorization
- `Transactions`: All financial transactions
- `SavingGoal`: Savings goals linked to accounts
- `Budget`: Budget tracking with time periods

## Development Notes

### Current Implementation

The application currently runs using the original `Complete_app.py` file for the GUI components to ensure full compatibility. The modular structure is in place for:

- ✅ Configuration (`config.py`)
- ✅ Data models (`models/`)
- ✅ Database layer (`database/`)
- 🔄 GUI components (structure ready, extraction pending)

### Future Improvements

1. **Complete GUI Extraction**: Move all GUI classes to modular structure
2. **Plugin Architecture**: Support for extensions and themes
3. **Export/Import**: Data backup and restore functionality
4. **Advanced Reports**: PDF generation and custom date ranges
5. **Multi-currency**: Support for different currencies
6. **Cloud Sync**: Optional cloud backup integration

## Usage

1. **First Run**: Register a new user account
2. **Dashboard**: View balance summary and recent transactions
3. **Accounts**: Manage your bank accounts, cash, and savings
4. **Categories**: Organize transactions by category
5. **Transactions**: Add income, expenses, and transfers
6. **Budgets**: Set spending limits and monitor progress
7. **Savings Goals**: Track progress toward financial targets
8. **Reports**: Generate financial summaries and charts

## File Descriptions

- **`main.py`**: Application entry point
- **`config.py`**: Centralized configuration settings
- **`models/__init__.py`**: Model imports and ValidationError exception
- **`models/*.py`**: Individual data model classes
- **`database/database.py`**: Complete database management with CRUD operations
- **`Complete_app.py`**: Original monolithic file (maintained for compatibility)

## Error Handling

The application includes comprehensive error handling:

- Database connection errors
- Validation failures
- GUI exceptions
- File I/O errors
- Network issues (future cloud features)

All errors are logged to `finance_app.log` with appropriate user notifications.

## Security

- Passwords are hashed with random salts
- SQL injection prevention through parameterized queries
- Input validation on all user data
- Session management for user authentication
- Secure database operations with transaction rollback

## Contributing

When contributing to this project:

1. Follow the modular structure
2. Add appropriate validation to models
3. Include comprehensive error handling
4. Write docstrings for all functions
5. Test database operations thoroughly
6. Maintain backwards compatibility

## License

This project is provided as-is for educational and personal use. 