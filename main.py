import tkinter as tk
mainbalance = 0
income = 0
expense = 0

def update_balance():
    balance.config(text = f"{mainbalance} BDT")
    income_label.config(text= f"{income} BDT")
    expense_label.config(text= f"{expense} BDT")

def add_income():
    global mainbalance, income
    value = int(input("Enter Income:\n"))
    mainbalance = value + mainbalance
    income = income + value

def add_expense():
    global mainbalance, expense
    value = int(input("Enter Expense:\n"))
    mainbalance = mainbalance - value
    expense = expense + value



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

cashFlo = tk.Label(master = frame1, text = "CashFlo", font = ('arial', 10), bg='orange')
cashFlo.grid(column = 0, row = 2, columnspan = 2, sticky = 'nsew')
 

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

window.mainloop()