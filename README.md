# 💰 Personal Finance Manager

A comprehensive desktop application to take control of your finances! Track expenses, manage budgets, set saving goals, and generate insightful reports - all in one place.

![Finance App](https://img.shields.io/badge/Python-3.7%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey)

## 🌟 Why This App?

Let's be honest - managing money can be overwhelming. Between multiple bank accounts, endless transactions, and those budgets we never stick to, it's easy to lose track of where our money goes. 

This app was built to solve that problem. It's not just another finance tracker; it's your personal financial assistant that helps you:

- **Actually stick to budgets** (with helpful warnings before you overspend)
- **Reach your saving goals** (with progress tracking that keeps you motivated)
- **Understand your spending patterns** (through beautiful charts and reports)
- **Keep everything organized** (no more scattered receipts and mental math)

## ✨ Features That Actually Matter

### 🏦 **Smart Account Management**
- Support for multiple account types (Bank, Cash, Savings)
- Real-time balance tracking across all accounts
- Easy money transfers between accounts

### 💸 **Effortless Transaction Tracking**
- Quick income and expense logging
- Customizable categories (Food, Transport, Entertainment, etc.)
- Transaction history with smart search and filtering

### 🎯 **Goal-Oriented Savings**
- Set and track multiple saving goals
- Visual progress indicators to keep you motivated
- Automatic calculations for target dates

### 📊 **Budget That Works**
- Weekly, monthly, or yearly budget planning
- Smart warnings when you're approaching limits
- Category-wise spending analysis

### 📈 **Insightful Reports**
- Beautiful charts showing spending trends
- Monthly summaries and category breakdowns
- Account performance tracking
- Export reports for tax season or personal records

### 🔒 **Privacy First**
- All data stored locally on your computer
- Secure password hashing
- No data sent to external servers

## 🚀 Getting Started

### Prerequisites

Make sure you have Python 3.7+ installed on your system. You can download it from [python.org](https://www.python.org/downloads/).

### Installation

1. **Clone this repository**
   ```bash
   git clone https://github.com/yourusername/personal-finance-manager.git
   cd personal-finance-manager
   ```

2. **Install required packages**
   ```bash
   pip install matplotlib
   ```
   *That's it! The app uses built-in Python libraries for everything else.*

3. **Run the application**
   ```bash
   python test.py
   ```

### First Time Setup

1. **Create your account** - The app will guide you through a simple registration process
2. **Set up your accounts** - Add your bank accounts, cash, and savings
3. **Add some categories** - Customize expense and income categories that match your lifestyle
4. **Start tracking** - Begin logging your transactions and watch your financial picture come together

## 🎯 How to Use

### Managing Your Money Flow

**Adding Income:**
- Click the "Income" button
- Select the account it's going into
- Choose a category (Salary, Freelance, etc.)
- Enter the amount and description

**Recording Expenses:**
- Hit "Expense" 
- Pick which account you're spending from
- Select the expense category
- Log the amount with a quick note

**Transferring Between Accounts:**
- Use "Transfer" to move money between your accounts
- Perfect for moving cash to savings or between bank accounts

### Setting Up Budgets That Work

1. Go to the "Budgets" tab
2. Choose a category you want to control (like "Food & Drink")
3. Set your spending limit and time period
4. The app will warn you when you're getting close to your limit

### Saving Goals Made Simple

1. Navigate to "Saving Goals"
2. Create a goal (vacation, emergency fund, new laptop, etc.)
3. Set your target amount
4. Watch your progress as you add money to your savings

### Understanding Your Finances

Head to the "Reports" tab to see:
- Where your money is actually going
- Trends in your spending over time
- How well you're sticking to budgets
- Progress on your saving goals

## 🛠️ Built With

- **Python** - The backbone of the application
- **Tkinter** - For the clean, intuitive user interface
- **SQLite** - Lightweight database for secure local storage
- **Matplotlib** - Beautiful charts and graphs for data visualization

## 📁 Project Structure

```
personal-finance-manager/
├── test.py              # Main application file (everything in one place!)
├── finance_app.db       # Your data (created automatically)
├── finance_app.log      # Application logs
└── README.md           # You're reading this now!
```

## 🔧 Troubleshooting

**App won't start?**
- Make sure you have Python 3.7+ installed
- Try deleting `finance_app.db` if you're getting database errors
- Check that matplotlib is installed: `pip install matplotlib`

**Data not saving?**
- Make sure you have write permissions in the app directory
- Check the logs in `finance_app.log` for any error messages

**Charts not displaying?**
- Ensure matplotlib is properly installed
- Some older systems might need: `pip install matplotlib --upgrade`

## 🤝 Contributing

Found a bug? Have a feature idea? I'd love to hear from you!

1. Fork the repository
2. Create a feature branch (`git checkout -b amazing-feature`)
3. Make your changes
4. Commit them (`git commit -m 'Add amazing feature'`)
5. Push to the branch (`git push origin amazing-feature`)
6. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 💡 Future Ideas

- [ ] Mobile app companion
- [ ] Cloud sync option (while keeping local-first approach)
- [ ] Investment tracking
- [ ] Bill reminders
- [ ] Multi-currency support
- [ ] Data import from bank statements

## 🙏 Acknowledgments

- Built with love for anyone trying to get their finances in order
- Inspired by the need for a simple, privacy-focused finance tracker
- Special thanks to the Python community for amazing libraries

---

**Ready to take control of your finances?** Download the app and start your journey toward financial clarity today! 🎉

*Remember: The best finance app is the one you actually use. This one is designed to be simple enough for daily use, yet powerful enough to give you real insights into your money.* 