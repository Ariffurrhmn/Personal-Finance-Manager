# Personal Finance Manager

A comprehensive personal finance management application built with Python and Tkinter. Track your income, expenses, savings goals, and budgets all in one place with an intuitive graphical interface.

## Features

### 🔐 User Management
- **Secure Authentication**: User registration and login with password hashing
- **Multi-user Support**: Each user has their own isolated financial data

### 💰 Account Management
- **Multiple Account Types**: Bank, Cash, and Savings accounts
- **Real-time Balance Tracking**: View total balance across all accounts
- **Account Operations**: Create, view, and delete accounts

### 📊 Transaction Management
- **Income Tracking**: Record income with categories and descriptions
- **Expense Tracking**: Track expenses by category with detailed records
- **Money Transfers**: Transfer funds between accounts
- **Transaction History**: Paginated view of all transactions with search

### 🎯 Savings Goals
- **Goal Setting**: Set target amounts for savings goals
- **Progress Tracking**: Visual progress bars and percentage completion
- **Goal Completion**: Celebrate achievements with completion notifications
- **Flexible Management**: Convert completed goals to regular accounts or delete them

### 📋 Budget Management
- **Category Budgets**: Set spending limits for different categories
- **Time Periods**: Monthly, weekly, or custom date range budgets
- **Budget Monitoring**: Real-time tracking of budget vs. actual spending
- **Warnings & Alerts**: Get notified when approaching or exceeding budget limits

### 📈 Financial Reports
- **Multiple Report Types**:
  - Monthly Summary
  - Category Analysis
  - Account Performance
  - Budget Analysis
  - Complete Financial Overview
- **Visual Charts**: Interactive charts for better data visualization


### 🏷️ Category Management
- **Income & Expense Categories**: Organize transactions by type
- **Custom Categories**: Create categories that fit your lifestyle
- **Category Analysis**: Track spending patterns by category

## Installation

### Prerequisites
- Python 3.7 or higher
- pip (Python package installer)

### Required Libraries
```bash
pip install matplotlib reportlab
```

### Quick Start
1. **Download the application**:
   ```bash
   git clone <repository-url>
   cd Personal-Finance-Manager
   ```

2. **Install dependencies**:
   ```bash
   pip install matplotlib reportlab
   ```

3. **Run the application**:
   ```bash
   python Complete_app.py
   ```

## Usage Guide

### First Time Setup
1. **Launch the application**
2. **Register a new account** with your email and password
3. **Login** with your credentials

### Getting Started
1. **Create Accounts**: Add your bank accounts, cash, or savings accounts
2. **Set Up Categories**: Create income and expense categories
3. **Record Transactions**: Start tracking your income and expenses
4. **Set Savings Goals**: Define what you're saving for
5. **Create Budgets**: Set spending limits for different categories

### Dashboard Overview
- **Balance Summary**: Quick overview of total balance across accounts
- **Recent Transactions**: Latest financial activities
- **Savings Progress**: Visual representation of goal progress
- **Budget Status**: Current budget performance

### Managing Transactions
- **Add Income**: Record salary, freelance work, or other income sources
- **Add Expenses**: Track daily expenses with categories and descriptions
- **Transfer Money**: Move funds between your accounts
- **View History**: Browse all transactions with pagination

### Savings Goals
- **Create Goals**: Set target amounts and optional account associations
- **Track Progress**: Monitor how close you are to achieving your goals
- **Goal Completion**: Get notified when goals are reached

### Budget Management
- **Set Budgets**: Define spending limits for categories
- **Monitor Spending**: Real-time tracking against budget limits
- **Receive Alerts**: Get warnings when approaching or exceeding budgets
- **Flexible Periods**: Set monthly, weekly, or custom time ranges

### Financial Reports
- **Generate Reports**: Create detailed financial analysis
- **Visual Charts**: View spending patterns and trends
- **Export to PDF**: Save reports for record-keeping
- **Custom Date Ranges**: Analyze specific time periods

## Technical Details

### Architecture
- **Single File Application**: Complete app in one Python file for easy deployment
- **SQLite Database**: Local database storage for all financial data
- **Tkinter GUI**: Native cross-platform graphical interface
- **Object-Oriented Design**: Clean, maintainable code structure

### Database Schema
- **Users**: Secure user authentication and profile data
- **Accounts**: Multiple account types with balance tracking
- **Categories**: Flexible categorization system
- **Transactions**: Comprehensive transaction logging
- **Saving Goals**: Goal tracking with progress monitoring
- **Budgets**: Budget management with time period support

### Security Features
- **Password Hashing**: Secure password storage using SHA-256 with salt
- **User Isolation**: Each user's data is completely separate
- **Input Validation**: Comprehensive validation for all user inputs

### Data Visualization
- **Matplotlib Integration**: Charts and graphs for financial analysis

## File Structure
```
Personal-Finance-Manager/
├── Complete_app.py          # Main application file
├── README.md               # This file
├── finance_manager.db      # SQLite database (created automatically)
└── reports/               # Generated PDF reports (created automatically)
```

## Configuration

### Default Settings
- **Database Path**: `finance_manager.db` (current directory)
- **Items per Page**: 10 transactions per page
- **Account Types**: Bank, Cash, Savings
- **Category Types**: Income, Expense
- **Budget Periods**: Month, Week, Custom

### Customization
You can modify the following constants in the code:
- `DB_PATH`: Database file location
- `ITEMS_PER_PAGE`: Number of items displayed per page
- `BUDGET_CONFIG`: Budget time periods and defaults

## Troubleshooting

### Common Issues

**1. Module Import Errors**
```bash
# Install missing dependencies
pip install matplotlib reportlab
```

**2. Database Errors**
- Ensure write permissions in the application directory
- Check if `finance_manager.db` is not locked by another process

**3. GUI Display Issues**
- Ensure you're running in a desktop environment with GUI support
- On Linux, you may need to install `python3-tk`

**4. PDF Report Generation**
- Verify ReportLab is installed: `pip install reportlab`
- Check write permissions for the reports directory

### Performance Notes
- The application creates database indexes for optimal performance
- Large transaction histories are handled with pagination
- Reports are generated efficiently with optimized queries

## Contributing

This is a single-file application designed for simplicity and portability. To contribute:

1. Fork the repository
2. Make your changes to `Complete_app.py`
3. Test thoroughly with different user scenarios
4. Submit a pull request with a clear description

## License

This project is available under the MIT License. See the LICENSE file for details.

## Support

For support, please:
1. Check the troubleshooting section above
2. Review the code comments for implementation details
3. Open an issue with detailed error information

**Made with ❤️ for better financial management** 