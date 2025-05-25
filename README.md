# Finance Management Application

A modern personal finance management application built with Python and Tkinter, featuring a clean architecture and comprehensive functionality for managing personal finances.

## 🚀 Quick Start

### Running the Application
```bash
python main.py
```

### Running Tests
```bash
python run_tests.py
```

## 📁 Project Structure

```
Finance-Management-App/
├── main.py                 # Application launcher
├── run_tests.py           # Test runner
├── requirements.txt       # Dependencies
├── README.md             # Documentation
├── src/                  # Source code
│   ├── __init__.py       # Package initialization
│   ├── app.py           # Main application controller
│   ├── config.py        # Configuration settings
│   ├── models.py        # Data models
│   ├── database.py      # Database layer
│   ├── ui_login.py      # Login/Register UI
│   └── ui_main.py       # Main application UI
├── tests/               # Test suite
│   └── test_finance_app.py
├── icons/               # Application icons
│   ├── 16x16.ico        # Small window icon
│   ├── 32x32.ico        # Standard window icon
│   ├── 48x48.ico        # Medium window icon
│   ├── 64x64.ico        # Large window icon (used by app)
│   ├── 128x128.ico      # Extra large icon
│   └── logo.png         # PNG logo for in-app display (optional)
├── finance_app.db       # SQLite database (created at runtime)
└── finance_app.log      # Application logs (created at runtime)
```

## ✨ Features

### 🔐 **User Management**
- Secure user registration and authentication
- Password hashing with salt for security
- Session management

### 💰 **Account Management**
- Multiple account types: **Bank**, **Cash**, **Internet Bank**
- Real-time balance tracking
- Account limit: Maximum 5 accounts per user
- Zero balance start for new accounts

### 📊 **Transaction Management**
- **Income tracking** with categorization
- **Expense tracking** with balance validation
- **Transfer between accounts** with balance checks
- Transaction history with detailed information
- Monthly income/expense summaries

### 🏷️ **Category Management**
- Custom income and expense categories
- Default categories provided
- Easy category management interface

### 📈 **Dashboard & Analytics**
- Real-time balance display
- Monthly cashflow analysis
- Transaction history with search
- Visual transaction categorization

### 🛡️ **Financial Logic & Validation**
- **Balance validation**: Cannot spend more than available
- **Account isolation**: Each account has independent balance
- **Transfer validation**: Prevents invalid transfers
- **Input validation**: Comprehensive data validation

## 🛠️ Installation

### Prerequisites
- Python 3.7 or higher
- No external dependencies required (uses Python standard library)

### Setup
1. **Clone or download** the project
2. **Navigate** to the project directory
3. **Run** the application:
   ```bash
   python main.py
   ```

## 📖 Usage Guide

### 1. **Getting Started**
- Run `python main.py`
- **Register** a new account or **login** with existing credentials
- Start with 2 default accounts (Bank and Cash) with 0 balance

### 2. **Adding Money (Income)**
- Click **"Add Income"** on the dashboard
- Select account, category, and enter amount
- Add description (optional)

### 3. **Recording Expenses**
- Click **"Add Expense"** on the dashboard
- Select source account (must have sufficient balance)
- Choose expense category and enter amount

### 4. **Transferring Between Accounts**
- Click **"Transfer Balance"** on the dashboard
- Select source and destination accounts
- Enter transfer amount (validates source balance)

### 5. **Managing Accounts**
- Go to **"Edit Accounts"** tab
- Add new accounts (up to 5 total)
- Delete accounts (with confirmation)

### 6. **Managing Categories**
- Go to **"Edit Categories"** tab
- Add custom income/expense categories
- Delete categories (with confirmation)

## 🏗️ Technical Architecture

### **Modular Design**
- **Separation of Concerns**: Models, Database, UI, and Configuration separated
- **Clean Architecture**: Each module has a single responsibility
- **Package Structure**: Organized in `src/` directory for maintainability

### **Database Layer**
- **SQLite** database with proper schema design
- **Foreign key relationships** with cascading deletes
- **Indexed queries** for performance
- **Transaction safety** with automatic rollback
- **Connection pooling** with context managers

### **Security Features**
- **Password hashing** with SHA-256 + random salt
- **SQL injection protection** with parameterized queries
- **Input validation** at model and UI levels
- **Session management** with proper logout

### **Error Handling**
- **Comprehensive exception handling** throughout the application
- **User-friendly error messages** with specific guidance
- **Logging system** for debugging and monitoring
- **Graceful degradation** for edge cases

### **Testing**
- **Unit tests** for all models and validation
- **Integration tests** for database operations
- **Workflow tests** for complete user scenarios
- **Test isolation** with temporary databases

## 🎨 UI/UX Features

### **Modern Interface**
- **Inter font** typography throughout
- **Consistent color scheme** with professional appearance
- **Responsive layout** with proper grid management
- **Intuitive navigation** with tabbed interface

### **User Experience**
- **Real-time updates** after each transaction
- **Keyboard shortcuts** (Enter key support)
- **Form validation** with immediate feedback
- **Confirmation dialogs** for destructive actions
- **Scrollable lists** with mouse wheel support

## 🔧 Configuration

The application can be customized through `src/config.py`:

- **Window settings**: Size, title, and appearance
- **Color scheme**: Complete color customization
- **Font configuration**: Typography settings
- **Validation rules**: Limits and constraints
- **Account limits**: Maximum accounts per user
- **Default data**: Starting accounts and categories

## 🧪 Testing

### **Running Tests**
```bash
python run_tests.py
```

### **Test Coverage**
- ✅ Model validation (User, Account, Category, Transaction)
- ✅ Database operations (CRUD for all entities)
- ✅ Authentication and security
- ✅ Balance validation and financial logic
- ✅ Account limits and constraints
- ✅ Complete user workflows
- ✅ Error handling and edge cases

## 📝 Development

### **Adding New Features**
1. **Models**: Add data models in `src/models.py`
2. **Database**: Extend database operations in `src/database.py`
3. **UI**: Create UI components in `src/ui_*.py`
4. **Tests**: Add tests in `tests/test_finance_app.py`

### **Code Style**
- **Type hints** for better code documentation
- **Docstrings** for all classes and methods
- **Error handling** with specific exceptions
- **Logging** for debugging and monitoring

## 🚀 Building Executable

This project is structured to be easily converted to an executable using tools like:
- **PyInstaller**
- **cx_Freeze**
- **auto-py-to-exe**

The modular structure and single entry point (`main.py`) make it ideal for packaging.

## 📄 License

This project is open source and available under the MIT License.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.

---

**Built with ❤️ using Python and Tkinter** 