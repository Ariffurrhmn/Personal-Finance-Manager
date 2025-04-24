import tkinter as tk

mainbalance = 0
income = 0
expense = 0
cashflow = 0

accounts = ['Cash', 'Bank', 'Bkash', 'Saving']
categories = ['Food & Drinks', 'Health', 'Groceries', 'Transport', 'Bill & Fees']
transactions = []  # Store transactions

def update_cashflow():
    global cashflow, income, expense
    cashflow = income - expense
    if cashflow >= 0:
        cashflow_label.config(text=f"+{cashflow} BDT", fg='green')
    else:
        cashflow_label.config(text=f"-{abs(cashflow)} BDT", fg='red')

def update_balance():
    balance.config(text=f"{mainbalance} BDT")
    income_value.config(text=f"{income} BDT")
    expense_value.config(text=f"{expense} BDT")
    update_cashflow()

def add_transaction_row(category, account, amount, description, ttype):
    row = len(transactions) + 1
    transactions.append((category, account, amount, description, ttype))

    for idx, text in enumerate([category, account, f"{amount} BDT", description, ttype]):
        label = tk.Label(transaction_snip, text=text, bg="#ffffff", font=('Arial', 11))
        label.grid(row=row, column=idx, sticky="nsew", padx=1, pady=1)

def add_income():
    income_prompt = tk.Toplevel(window)
    income_prompt.geometry('400x350')
    income_prompt.title("Add Income")

    for i in range(4):
        income_prompt.rowconfigure(i, weight=1, uniform='a')
    income_prompt.columnconfigure((0, 1), weight=1, uniform='a')

    tk.Label(income_prompt, text="Account:", font=('arial', 12)).grid(row=0, column=0, sticky='e', padx=10, pady=5)
    account_var = tk.StringVar(value=accounts[0])
    tk.OptionMenu(income_prompt, account_var, *accounts).grid(row=0, column=1, padx=10, pady=5)

    tk.Label(income_prompt, text="Description:", font=('arial', 12)).grid(row=1, column=0, sticky='e', padx=10, pady=5)
    description_entry = tk.Entry(income_prompt, font=('arial', 12))
    description_entry.grid(row=1, column=1, padx=10, pady=5)

    tk.Label(income_prompt, text="Amount:", font=('arial', 12)).grid(row=2, column=0, sticky='e', padx=10, pady=5)
    amount_entry = tk.Entry(income_prompt, font=('arial', 12), bg='lightgreen')
    amount_entry.grid(row=2, column=1, padx=10, pady=5)

    def submit_income():
        global mainbalance, income
        try:
            amount = float(amount_entry.get())
            account = account_var.get()
            description = description_entry.get()

            mainbalance += amount
            income += amount
            update_balance()
            add_transaction_row("-", account, amount, description, "Income")
            income_prompt.destroy()
        except ValueError:
            print("Invalid amount")

    tk.Button(income_prompt, text="Add Income", font=('arial', 12), command=submit_income, bg='green', fg='white').grid(row=3, column=0, columnspan=2, pady=10)

def add_expense():
    expense_prompt = tk.Toplevel(window)
    expense_prompt.geometry('400x400')
    expense_prompt.title("Add Expense")

    for i in range(5):
        expense_prompt.rowconfigure(i, weight=1, uniform='a')
    expense_prompt.columnconfigure((0, 1), weight=1, uniform='a')

    tk.Label(expense_prompt, text="Category:", font=('arial', 12)).grid(row=0, column=0, sticky='e', padx=10, pady=5)
    category_var = tk.StringVar(value=categories[0])
    tk.OptionMenu(expense_prompt, category_var, *categories).grid(row=0, column=1, padx=10, pady=5)

    tk.Label(expense_prompt, text="Account:", font=('arial', 12)).grid(row=1, column=0, sticky='e', padx=10, pady=5)
    account_var = tk.StringVar(value=accounts[0])
    tk.OptionMenu(expense_prompt, account_var, *accounts).grid(row=1, column=1, padx=10, pady=5)

    tk.Label(expense_prompt, text="Description:", font=('arial', 12)).grid(row=2, column=0, sticky='e', padx=10, pady=5)
    description_entry = tk.Entry(expense_prompt, font=('arial', 12))
    description_entry.grid(row=2, column=1, padx=10, pady=5)

    tk.Label(expense_prompt, text="Amount:", font=('arial', 12)).grid(row=3, column=0, sticky='e', padx=10, pady=5)
    amount_entry = tk.Entry(expense_prompt, font=('arial', 12), bg='lightcoral')
    amount_entry.grid(row=3, column=1, padx=10, pady=5)

    def submit_expense():
        global mainbalance, expense
        try:
            amount = float(amount_entry.get())
            category = category_var.get()
            account = account_var.get()
            description = description_entry.get()

            mainbalance -= amount
            expense += amount
            update_balance()
            add_transaction_row(category, account, amount, description, "Expense")
            expense_prompt.destroy()
        except ValueError:
            print("Invalid amount")

    tk.Button(expense_prompt, text="Add Expense", font=('arial', 12), command=submit_expense, bg='red', fg='white').grid(row=4, column=0, columnspan=2, pady=10)


window = tk.Tk()
window.geometry("800x600")

frame1 = tk.Frame(window, bg='lightyellow')
frame1.pack(fill='x')

balance = tk.Label(frame1, text=f"{mainbalance} BDT", font=('Arial', 20), bg='lightyellow')
balance.pack(side='top', pady=5)

income_value = tk.Label(frame1, text=f"{income} BDT", font=('Arial', 12), bg='white')
income_value.pack(side='left', padx=10)

expense_value = tk.Label(frame1, text=f"{expense} BDT", font=('Arial', 12), bg='white')
expense_value.pack(side='left', padx=10)

cashflow_label = tk.Label(frame1, text=f"{cashflow} BDT", font=('Arial', 12), bg='white')
cashflow_label.pack(side='right', padx=10)

tk.Button(frame1, text="Add Income", command=add_income).pack(side='left', padx=10)
tk.Button(frame1, text="Add Expense", command=add_expense).pack(side='left', padx=10)

transaction_snip = tk.Frame(window, relief="groove", bg="#f8f9fa", bd=1)
transaction_snip.pack(fill='both', expand=True, padx=10, pady=10)

for i in range(5):
    transaction_snip.columnconfigure(i, weight=1)

titles = ["Category", "Account", "Amount", "Description", "Type"]
for col, title in enumerate(titles):
    tk.Label(transaction_snip, text=title, bg="#dee2e6", font=('Arial', 12, 'bold')).grid(row=0, column=col, sticky="nsew", padx=1, pady=1)

window.mainloop()
