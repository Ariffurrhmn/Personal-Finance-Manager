# Personal Finance Manager

A comprehensive desktop application built with Python and Tkinter to help individuals track their income, expenses, and savings while promoting financial literacy and better money management.

## Team Members

| Name | Student ID | Role |
|------|------------|------|
| **Arifur Rahman** | 20234103222 | Developer - Full implementation of UI and backend code integration |
| **Sumi Akter** | 20234103255 | Database Administrator - Database design, queries, and data management |
| **Akhi Akter** | 20234103212 | UI/UX Designer - Visual interface design and user experience |
| **Sheikh Md. Fahad** | 20234103238 | QA Specialist - Quality assurance, testing, and improvement feedback |
| **Parvez Hasan Sharif** | 20234103228 | Report Generation Specialist - Financial data structure and display |

## Project Motivation

This project was initially suggested by our course instructor to build a basic personal finance tracker. However, our motivation grew stronger after observing how financial challenges affect students in real life. Many students living independently on limited incomes struggled to manage money effectively.

The project was inspired by the real need for a tool that promotes better financial habits. By allowing users to track income, expenses, and savings, the app helps people gain clearer understanding of their financial health. The savings section was specifically added to encourage financial discipline, separating saved amounts from daily spending.

Our goal is to make personal finance less overwhelming and more manageable for everyone.

## Features

### 🔐 User Registration and Authentication
- Secure user login and registration system
- Email verification and password hashing for data protection
- Multi-user support with individual data isolation

### 💰 Account Management
- Create, edit, and delete different account types (Bank, Cash, Savings)
- Real-time balance tracking across all accounts
- Account categorization for better organization

### 📊 Transaction Management
- Comprehensive income and expense tracking
- Add, edit, and delete transactions with detailed categorization
- Support for transfers between accounts
- Transaction history with search and filter capabilities

### 📈 Budget Management
- Set up budgets for specific categories
- Track spending progress against budget limits
- Visual indicators for budget status (under/over budget)
- Monthly and custom period budget tracking

### 🎯 Saving Goals
- Create and monitor saving goals
- Progress tracking towards goal completion
- Visual progress indicators
- Goal deadline management

### 📋 Reports Generation
- Monthly income and expense reports
- Category-wise spending analysis
- Visual charts and graphs using Matplotlib
- Export capabilities for financial data

### 🎨 Modern UI/UX
- Clean, intuitive interface designed for ease of use
- Responsive design with proper font fallback system
- Color-coded elements for better visual organization
- User-friendly navigation and workflow

## Technical Stack

### Programming Language
- **Python 3** - Complete application development including UI, backend, and database interactions

### UI Framework
- **Tkinter** - Cross-platform GUI framework for desktop application interface

### Database
- **SQLite** - Lightweight relational database for storing:
  - User accounts and authentication data
  - Financial accounts and transaction history
  - Categories, budgets, and saving goals
  - Application logs and preferences

### Data Visualization
- **Matplotlib** - Chart generation and financial data visualization for reports and analytics

### Security
- **Hashlib & Secrets** - Password hashing with salt encryption for secure user authentication

### Development Environment
- **VS Code** - Primary IDE for development, testing, and debugging

## Database Structure

The application uses a normalized SQLite database with the following tables:

- **User** - User accounts with hashed passwords
- **Account** - Financial accounts (checking, savings, etc.)
- **Category** - Transaction categories for organization
- **Transactions** - All financial transactions with type classification
- **SavingGoal** - User-defined savings targets
- **Budget** - Category-based budget limits

## Installation & Setup

### Prerequisites
- Python 3.7 or higher
- Required Python packages (automatically installed):
  - tkinter (usually included with Python)
  - matplotlib
  - sqlite3 (included with Python)

### Installation Steps

1. **Clone or download the repository:**
   ```bash
   git clone [repository-url]
   cd Personal-Finance-Manager
   ```

2. **Install dependencies:**
   ```bash
   pip install matplotlib
   ```

3. **Run the application:**
   ```bash
   python Complete_app.py
   ```

## Usage Guide

### First Time Setup
1. Launch the application
2. Create a new user account with email and secure password
3. Set up your initial accounts (checking, savings, etc.)
4. Add your first transactions to get started

### Daily Usage
1. **Adding Transactions**: Record income, expenses, and transfers
2. **Managing Budgets**: Set monthly spending limits for categories
3. **Tracking Goals**: Monitor progress towards savings targets
4. **Viewing Reports**: Analyze spending patterns and financial health

### Sample Users
The application includes sample data for testing:
- **Sumi Smart**: Demonstrates good financial habits with regular savings
- **Mike Spender**: Shows challenging financial patterns for comparison

Both users have the password: `password123`

## Key Benefits

- **Financial Awareness**: Clear visibility into spending patterns
- **Budget Control**: Prevent overspending with category-based budgets
- **Savings Motivation**: Goal tracking encourages consistent saving habits
- **Data Security**: Local SQLite database keeps your financial data private
- **User-Friendly**: Intuitive interface suitable for all experience levels

## File Structure

```
Personal-Finance-Manager/
├── Complete_app.py          # Main application file
├── finance_app.db          # SQLite database
├── finance_app.log         # Application logs
├── README.md              # This documentation
└── SampleUsers.txt        # Sample user credentials
```

## Contributing

This project was developed as part of an academic assignment. For improvements or bug reports, please contact the development team.

## License

This project is developed for educational purposes as part of coursework requirements.

---

**Developed by Team Personal Finance Manager**  
*Making personal finance management accessible and effective for everyone* 