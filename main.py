import tkinter as tk
mainbalance = 0
income = 0
expense = 0
cashflow = 0

accounts = ['Cash', 'Bank', 'Bkash','Saving']
categories  = ['Food & Drinks', 'Health', 'Groceries','Transport', 'Bill & Fees']


def update_cashflow():
    global cashflow, income, expense
    cashflow = income - expense
    if cashflow >= 0:
        cashflow_label.config(text= f"+{cashflow} BDT", fg='green')
    else:
        cashflow_label.config(text= f"-{cashflow} BDT", fg='red')

def update_balance():
    balance.config(text = f"{mainbalance} BDT")
    income_value.config(text= f"{income} BDT")
    expense_value.config(text= f"{expense} BDT")
    update_cashflow()

def add_income():
    income_prompt = tk.Toplevel(window)
    income_prompt.geometry('400x350')
    income_prompt.title("Add Income")

    income_prompt.rowconfigure((0,1), weight = 1, uniform='a')
    income_prompt.rowconfigure(2, weight=2, uniform='a')
    income_prompt.columnconfigure(0, weight=1, uniform='a')
    income_prompt.columnconfigure(1, weight=2, uniform='a')

    #account option
    account_label = tk.Label(income_prompt, text="Account:", font = ('arial', 12))
    account_label.grid(row = 0, column=0, sticky='e', padx=10, pady=5)
    account_var = tk.StringVar()
    account_menu = tk.OptionMenu(income_prompt, account_var, *accounts)
    account_menu.grid(row = 0, column=1,  padx=10, pady=5)

    # Description Entry
    description_label = tk.Label(income_prompt, text="Description:", font=('arial', 12))
    description_label.grid(row=1, column=0, sticky='e', padx=10, pady=5)
    description_entry = tk.Entry(income_prompt, font=('arial', 12))
    description_entry.grid(row=1, column=1, padx=10, pady=5)

    # Amount Entry (Green background for Income)
    amount_label = tk.Label(income_prompt, text="Amount:", font=('arial', 12))
    amount_label.grid(row=2, column=0, sticky='e', padx=10, pady=5)
    amount_entry = tk.Entry(income_prompt, font=('arial', 12), bg='lightgreen')  # Light green for income
    amount_entry.grid(row=2, column=1, padx=10, pady=5)

    #submit button
    def submit_income():
        global mainbalance, income
        try:
            amount = float(amount_entry.get())
            account = account_var.get()
            description = description_entry.get()

            mainbalance += amount
            income += amount
            update_balance()

            # Output to console
            print(f"Income Added: Account: {account}, Description: {description}, Amount: {amount} BDT")

            income_prompt.destroy()
        except ValueError:
            print("Please enter a valid amount.")

    submit_button = tk.Button(income_prompt, text="Add Income", font=('arial', 12), command=submit_income, bg='green', fg='white')  # Green button
    submit_button.grid(row=4, column=0, columnspan=2, pady=10)

def add_expense():
    expense_prompt = tk.Toplevel(window)
    expense_prompt.geometry('400x350')
    expense_prompt.title("Add Expense")

    expense_prompt.rowconfigure((0, 1, 2), weight=1, uniform='a')
    expense_prompt.rowconfigure(3, weight=2, uniform='a')
    expense_prompt.columnconfigure(0, weight=1, uniform='a')
    expense_prompt.columnconfigure(1, weight=2, uniform='a')

    # Category Dropdown
    category_label = tk.Label(expense_prompt, text="Category:", font=('arial', 12))
    category_label.grid(row=0, column=0, sticky='e', padx=10, pady=5)
    category_var = tk.StringVar()
    category_menu = tk.OptionMenu(expense_prompt, category_var, *categories)
    category_menu.grid(row=0, column=1, padx=10, pady=5)

    # Account Dropdown
    account_label = tk.Label(expense_prompt, text="Account:", font=('arial', 12))
    account_label.grid(row=1, column=0, sticky='e', padx=10, pady=5)
    account_var = tk.StringVar()
    account_menu = tk.OptionMenu(expense_prompt, account_var, *accounts)
    account_menu.grid(row=1, column=1, padx=10, pady=5)

    # Description Entry
    description_label = tk.Label(expense_prompt, text="Description:", font=('arial', 12))
    description_label.grid(row=2, column=0, sticky='e', padx=10, pady=5)
    description_entry = tk.Entry(expense_prompt, font=('arial', 12))
    description_entry.grid(row=2, column=1, padx=10, pady=5)

    # Amount Entry (Red background for Expense)
    amount_label = tk.Label(expense_prompt, text="Amount:", font=('arial', 12))
    amount_label.grid(row=3, column=0, sticky='e', padx=10, pady=5)
    amount_entry = tk.Entry(expense_prompt, font=('arial', 12), bg='lightcoral')  # Light red for expense
    amount_entry.grid(row=3, column=1, padx=10, pady=5)

    # Submit Button to add expense (Red Button)
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

            # Output to console
            print(f"Expense Added: Category: {category}, Account: {account}, Description: {description}, Amount: {amount} BDT")

            expense_prompt.destroy()
        except ValueError:
            print("Please enter a valid amount.")

    submit_button = tk.Button(expense_prompt, text="Add Expense", font=('arial', 12), command=submit_expense, bg='red', fg='white')  # Red button
    submit_button.grid(row=4, column=0, columnspan=2, pady=10)



window = tk.Tk()
window.geometry("720x720")

window.rowconfigure((0,1), weight=1, uniform='a')
window.columnconfigure((0,1), weight=1,uniform='a')

#grids
frame1 = tk.Frame(master=window, bg='yellow')
frame1.grid(column=0,row=0, sticky='nsew')

frame2 = tk.Frame(master=window, bg='blue')
frame2.grid(column=1,row=0, sticky='nsew')

frame3 = tk.Frame(master=window, bg='green')
frame3.grid(column=0,row=1, sticky='nsew')

frame4 = tk.Frame(master=window, bg='yellow')
frame4.grid(column=1,row=1, sticky='nsew')

#Balance, cashflow Frame1 
frame1.rowconfigure(0,weight=3, uniform='a')
frame1.rowconfigure(1,weight=1, uniform='a')
frame1.rowconfigure(2,weight=1, uniform='a')
frame1.columnconfigure((0,1),weight=1, uniform='a')

balance = tk.Label(master = frame1, text = f"{mainbalance} BDT", font = ('arial', 40), bg='yellow')
balance.grid(column = 0, row = 0, columnspan = 2, sticky = 'w')

#Income Tab
income_card = tk.Frame(master=frame1, bg='white')
income_card.grid(column=0,row=1, sticky="nsew")
income_card.columnconfigure(0, weight=1, uniform='a')  # Ensure column is set to expand
income_card.rowconfigure((0, 1, 2), weight=1, uniform='a')  # Ensure rows expand

# Income label
income_label = tk.Label(master=income_card, text="Income of this month:", font=('arial', 12), bg="white")
income_label.grid(column=0, row=0, sticky='w')

# Income value label
income_value = tk.Label(master=income_card, text=f"{income} BDT", font=('arial', 12), bg="white")
income_value.grid(column=0, row=1, sticky="nsew")

# Add income button
add_income = tk.Button(master=income_card, text="Add Income", font=('arial', 10), bg="white", command=add_income)
add_income.grid(column=0, row=2, sticky="nsew")

#Expense Tab
expense_card = tk.Frame(master=frame1, bg='white')
expense_card.grid(column=1,row=1, sticky="nsew")
expense_card.columnconfigure(0, weight=1, uniform='a')  # Ensure column is set to expand
expense_card.rowconfigure((0, 1, 2), weight=1, uniform='a')  # Ensure rows expand

# Income label
expense_label = tk.Label(master=expense_card, text="Expense of this month:", font=('arial', 12), bg="white")
expense_label.grid(column=0, row=0, sticky='w')

# Income value label
expense_value = tk.Label(master=expense_card, text=f"{expense} BDT", font=('arial', 12), bg="white")
expense_value.grid(column=0, row=1, sticky="nsew")

# Add income button
add_expense = tk.Button(master=expense_card, text="Add Expense", font=('arial', 10), bg="white", command=add_expense)
add_expense.grid(column=0, row=2, sticky="nsew")

cashflow_label = tk.Label(master = frame1, text = f"{cashflow}", font = ('arial', 10), bg='orange')
cashflow_label.grid(column = 0, row = 2, columnspan = 2, sticky = 'nsew')

#
# 
# 
# 
# 
# 
# 
#  


#Transactions frame3
frame3.columnconfigure(0, weight=1, uniform='a')
frame3.rowconfigure((0,1,2,3,4), weight=1, uniform='a')

transaction_snip = tk.Frame(master=frame3, relief="ridge", bg="gray")
transaction_snip.grid(column=0,row=0, sticky="nsew")

transaction_snip.rowconfigure((0,1),weight=1,uniform='a')
transaction_snip.columnconfigure((0,1),weight=1,uniform='a')

##########################
Category = tk.Label(master=transaction_snip, text='Category', fg="goldenrod1", font=('arial', 15), bg="gray")
Category.grid(column=0, row=0, sticky='nw')

account = tk.Label(master=transaction_snip, text='Account', fg="cyan2", font=('arial', 15), bg="gray")
account.grid(column=0, row=0, sticky='ne')

ammount = tk.Label(master=transaction_snip, text='$$$$', fg="green yellow", font=('arial', 15), bg="gray")
ammount.grid(column=0, row=1, sticky='sw')

tag = tk.Label(master=transaction_snip, text="'TAG'", fg="black", font=('arial', 15), bg="gray")
tag.grid(column=1, row=1, sticky='nsew')


# Goal-Tracker Frame2
frame2.columnconfigure(0, weight=1, uniform='a')
frame2.rowconfigure((0,1,2,3), weight=1, uniform='a')

goal_card = tk.Frame(master=frame2, relief="ridge", bg="gray")
goal_card.grid(column=0,row=0, sticky="nsew") 

goal_card.rowconfigure((0,1),weight=1,uniform='a')
goal_card.columnconfigure((0,1),weight=1,uniform='a')

#############################
goal_name = tk.Label(master=goal_card, text='Goal Name', fg="lawn green", font=('arial', 15), bg="gray")
goal_name.grid(column=0, row=0, sticky='nw')

status = tk.Label(master=goal_card, text='Target / Saved / To-go', fg="gold", font=('arial', 12), bg="gray")
status.grid(column=0, row=0, rowspan = 2, sticky='w')

progressbar = tk.Label(master=goal_card, text='/////////////////', fg="green2", font=('arial', 12), bg="gray")
progressbar.grid(column=0, row=1, rowspan = 1, sticky='w')


#Budget Summary Frame4
frame4.columnconfigure(0, weight=1, uniform='a')
frame4.rowconfigure(0, weight=1, uniform='a')
frame4.rowconfigure((1,2,3), weight=2, uniform='a')

budget_card = tk.Frame(master=frame4, relief="ridge", bg="lightgray")
budget_card.grid(column=0, row=0, sticky="nsew")

budget_card.rowconfigure((0, 1), weight=1, uniform='a')
budget_card.columnconfigure((0, 1, 2, 3), weight=1, uniform='a')

##############################
category_label = tk.Label(master=budget_card, text="Category", fg="green", font=('Arial', 15), bg="lightgray", relief="groove")
category_label.grid(column=0, row=0, sticky='nsew')

budgeted_label = tk.Label(master=budget_card, text="Budgeted", fg="cyan", font=('Arial', 15), bg="lightgray", relief="groove")
budgeted_label.grid(column=1, row=0, sticky='nsew')

actual_label = tk.Label(master=budget_card, text="Actual", fg="gold", font=('Arial', 15), bg="lightgray", relief="groove")
actual_label.grid(column=2, row=0, sticky='nsew')

remaining_label = tk.Label(master=budget_card, text="Remaining", fg="red", font=('Arial', 15), bg="lightgray", relief="groove")
remaining_label.grid(column=3, row=0, sticky='nsew')

#
#
#
#
#
#

window.mainloop()