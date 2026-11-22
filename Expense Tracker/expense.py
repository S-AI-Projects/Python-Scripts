import csv
import datetime
import os
import sqlite3

try:
    from tkcalendar import DateEntry
except ImportError:
    DateEntry = None

try:
    from tkinter import *
    from tkinter.filedialog import asksaveasfilename
    import tkinter.messagebox as tb
    import tkinter.ttk as ttk
except (ImportError, ModuleNotFoundError):
    # Fallbacks for headless/non-Tk environments
    END = 'end'
    TOP = 'top'
    X = 'x'
    Y = 'y'
    BOTTOM = 'bottom'
    RIGHT = 'right'
    CENTER = 'center'
    NO = 'no'
    HORIZONTAL = 'horizontal'
    VERTICAL = 'vertical'
    BROWSE = 'browse'
    tb = None
    ttk = None
    asksaveasfilename = None
    Tk = None
    Frame = None
    Label = None
    Entry = None
    Button = None
    OptionMenu = None
    Scrollbar = None
    StringVar = None
    DoubleVar = None


# Module-level references retained for backwards compatibility
connector = None
cursor = None
root = None
table = None
Desc = None
amnt = None
payee = None
MoP = None
date = None
date_from = None
date_to = None


def init_db(db_path="Expense Tracker.db"):
    """Initialize database connection and ensure ExpenseTracker table exists.

    Args:
        db_path (str): Path to SQLite database file or ':memory:'. Defaults to 'Expense Tracker.db'.

    Returns:
        tuple: (sqlite3.Connection, sqlite3.Cursor)
    """
    global connector, cursor
    conn = sqlite3.connect(db_path)
    conn.execute(
        'CREATE TABLE IF NOT EXISTS ExpenseTracker ('
        'ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, '
        'Date DATETIME, '
        'Payee TEXT, '
        'Description TEXT, '
        'Amount FLOAT, '
        'ModeOfPayment TEXT)'
    )
    conn.commit()
    cur = conn.cursor()
    connector = conn
    cursor = cur
    return conn, cur


# Functions
def list_all_expenses(conn=None, tree=None):
    """Fetch all expense records from the database and populate the treeview table.

    Public Inputs:
        conn (sqlite3.Connection, optional): SQLite connection. Defaults to global connector.
        tree (ttk.Treeview, optional): Treeview UI table. Defaults to global table.

    Result:
        list: All fetched records as a list of tuples from ExpenseTracker table.

    Mutation Behavior:
        - Deletes all existing child items from tree via tree.delete(*tree.get_children()).
        - Inserts each fetched row from the database into tree via tree.insert('', END, values=values).
        - Database rows are read-only and not mutated.

    External Dependencies:
        - SQLite database connection supporting execute() and fetchall().
        - Tkinter ttk.Treeview widget (or mock) supporting get_children(), delete(), and insert().
    """
    global connector, table
    active_conn = conn if conn is not None else connector
    active_table = tree if tree is not None else table

    if active_table is not None and hasattr(active_table, "get_children"):
        active_table.delete(*active_table.get_children())

    if active_conn is not None:
        all_data = active_conn.execute('SELECT * FROM ExpenseTracker')
        data = all_data.fetchall()
    else:
        data = []

    if active_table is not None and hasattr(active_table, "insert"):
        for values in data:
            active_table.insert('', END, values=values)

    return data


def clear_fields(desc_var=None, payee_var=None, amnt_var=None, mop_var=None, date_widget=None, tree=None):
    """Reset data entry form inputs and clear table selections."""
    global Desc, payee, amnt, MoP, date, table

    active_desc = desc_var if desc_var is not None else Desc
    active_payee = payee_var if payee_var is not None else payee
    active_amnt = amnt_var if amnt_var is not None else amnt
    active_mop = mop_var if mop_var is not None else MoP
    active_date = date_widget if date_widget is not None else date
    active_table = tree if tree is not None else table

    today_date = datetime.datetime.now().date()

    if active_desc is not None and hasattr(active_desc, 'set'):
        active_desc.set('')
    if active_payee is not None and hasattr(active_payee, 'set'):
        active_payee.set('')
    if active_amnt is not None and hasattr(active_amnt, 'set'):
        active_amnt.set(0.0)
    if active_mop is not None and hasattr(active_mop, 'set'):
        active_mop.set('Cash')
    if active_date is not None and hasattr(active_date, 'set_date'):
        active_date.set_date(today_date)
    if active_table is not None and hasattr(active_table, 'selection'):
        active_table.selection_remove(*active_table.selection())


def remove_expense(conn=None, tree=None, show_confirm=True):
    """Remove the currently selected expense from the table and database."""
    global connector, table
    active_conn = conn if conn is not None else connector
    active_table = tree if tree is not None else table

    if active_table is None or not hasattr(active_table, 'selection') or not active_table.selection():
        if tb is not None:
            tb.showerror('No record selected!', 'Please select a record to delete!')
        return False

    current_selected_expense = active_table.item(active_table.focus())
    values_selected = current_selected_expense['values']

    surety = True
    if show_confirm and tb is not None:
        surety = tb.askyesno('Are you sure?', f'Are you sure that you want to delete the record of {values_selected[2]}')

    if surety:
        if active_conn is not None:
            active_conn.execute('DELETE FROM ExpenseTracker WHERE ID=%d' % values_selected[0])
            active_conn.commit()

        list_all_expenses(conn=active_conn, tree=active_table)
        if tb is not None:
            tb.showinfo('Record deleted successfully!', 'The record you wanted to delete has been deleted successfully')
        return True
    return False


def remove_all_expenses(conn=None, tree=None, show_confirm=True):
    """Remove all expense records from the database and table."""
    global connector, table
    active_conn = conn if conn is not None else connector
    active_table = tree if tree is not None else table

    surety = True
    if show_confirm and tb is not None:
        surety = tb.askyesno('Are you sure?', 'Are you sure that you want to delete all the expense items from the database?', icon='warning')

    if surety:
        if active_table is not None and hasattr(active_table, 'get_children'):
            active_table.delete(*active_table.get_children())

        if active_conn is not None:
            active_conn.execute('DELETE FROM ExpenseTracker')
            active_conn.commit()

        clear_fields(tree=active_table)
        list_all_expenses(conn=active_conn, tree=active_table)
        if tb is not None:
            tb.showinfo('All Expenses deleted', 'All the expenses were successfully deleted')
        return True
    else:
        if tb is not None:
            tb.showinfo('Ok then', 'The task was aborted and no expense was deleted!')
        return False


def search_expenses(search_term, conn=None, tree=None):
    """Search and display expenses based on a search term in any column."""
    global connector, table
    active_conn = conn if conn is not None else connector
    active_table = tree if tree is not None else table

    if active_table is not None and hasattr(active_table, 'get_children'):
        active_table.delete(*active_table.get_children())

    query = """
    SELECT * FROM ExpenseTracker WHERE 
    Date LIKE ? OR 
    Payee LIKE ? OR 
    Description LIKE ? OR 
    Amount LIKE ? OR 
    ModeOfPayment LIKE ?;
    """
    search_param = f"%{search_term}%"
    results = []
    if active_conn is not None:
        cursor_res = active_conn.execute(query, (search_param,) * 5)
        results = cursor_res.fetchall()

    if active_table is not None and hasattr(active_table, 'insert'):
        for data in results:
            active_table.insert('', END, values=data)

    return results


def filter_expenses_by_date(date_from_val, date_to_val, conn=None, tree=None):
    """Filter and display expenses based on a date range."""
    global connector, table
    active_conn = conn if conn is not None else connector
    active_table = tree if tree is not None else table

    if active_table is not None and hasattr(active_table, 'get_children'):
        active_table.delete(*active_table.get_children())

    query = """
    SELECT * FROM ExpenseTracker WHERE Date BETWEEN ? AND ?;
    """
    results = []
    if active_conn is not None:
        cursor_res = active_conn.execute(query, (str(date_from_val), str(date_to_val)))
        results = cursor_res.fetchall()

    if active_table is not None and hasattr(active_table, 'insert'):
        for data in results:
            active_table.insert('', END, values=data)

    return results


def sort_expenses(column, order, conn=None, tree=None):
    """Sort expenses by a column in ascending or descending order."""
    global connector, table
    active_conn = conn if conn is not None else connector
    active_table = tree if tree is not None else table

    if active_table is not None and hasattr(active_table, 'get_children'):
        active_table.delete(*active_table.get_children())

    valid_columns = {'ID', 'Date', 'Payee', 'Description', 'Amount', 'ModeOfPayment'}
    valid_orders = {'ASC', 'DESC'}

    col_cleaned = column if column in valid_columns else 'ID'
    ord_cleaned = order.upper() if order.upper() in valid_orders else 'ASC'

    query = f"SELECT * FROM ExpenseTracker ORDER BY {col_cleaned} {ord_cleaned};"
    results = []
    if active_conn is not None:
        cursor_res = active_conn.execute(query)
        results = cursor_res.fetchall()

    if active_table is not None and hasattr(active_table, 'insert'):
        for data in results:
            active_table.insert('', END, values=data)

    return results


def add_another_expense(date_widget=None, payee_var=None, desc_var=None, amnt_var=None, mop_var=None, conn=None, tree=None):
    """Add a new expense to database using form values and refresh view."""
    global date, payee, Desc, amnt, MoP, connector, table

    active_date = date_widget if date_widget is not None else date
    active_payee = payee_var if payee_var is not None else payee
    active_desc = desc_var if desc_var is not None else Desc
    active_amnt = amnt_var if amnt_var is not None else amnt
    active_mop = mop_var if mop_var is not None else MoP
    active_conn = conn if conn is not None else connector
    active_table = tree if tree is not None else table

    date_val = active_date.get() if active_date and hasattr(active_date, 'get') else ''
    payee_val = active_payee.get() if active_payee and hasattr(active_payee, 'get') else ''
    desc_val = active_desc.get() if active_desc and hasattr(active_desc, 'get') else ''
    amnt_val = active_amnt.get() if active_amnt and hasattr(active_amnt, 'get') else ''
    mop_val = active_mop.get() if active_mop and hasattr(active_mop, 'get') else ''

    if not date_val or not payee_val or not desc_val or not amnt_val or not mop_val:
        if tb is not None:
            tb.showerror('Fields empty!', "Please fill all the missing fields before pressing the add button!")
        return False
    else:
        date_record = active_date.get_date() if hasattr(active_date, 'get_date') else date_val
        if active_conn is not None:
            active_conn.execute(
                'INSERT INTO ExpenseTracker (Date, Payee, Description, Amount, ModeOfPayment) VALUES (?, ?, ?, ?, ?)',
                (str(date_record), str(payee_val), str(desc_val), float(amnt_val), str(mop_val))
            )
            active_conn.commit()

        clear_fields(desc_var=active_desc, payee_var=active_payee, amnt_var=active_amnt, mop_var=active_mop, date_widget=active_date, tree=active_table)
        list_all_expenses(conn=active_conn, tree=active_table)
        if tb is not None:
            tb.showinfo('Expense added', 'The expense whose details you just entered has been added to the database')
        return True


def expense_to_words_before_adding(date_widget=None, desc_var=None, amnt_var=None, payee_var=None, mop_var=None, conn=None, tree=None):
    """Generate verbal description of expense and ask user confirmation before adding."""
    global date, Desc, amnt, payee, MoP
    active_date = date_widget if date_widget is not None else date
    active_desc = desc_var if desc_var is not None else Desc
    active_amnt = amnt_var if amnt_var is not None else amnt
    active_payee = payee_var if payee_var is not None else payee
    active_mop = mop_var if mop_var is not None else MoP

    date_val = active_date.get() if active_date and hasattr(active_date, 'get') else ''
    desc_val = active_desc.get() if active_desc and hasattr(active_desc, 'get') else ''
    amnt_val = active_amnt.get() if active_amnt and hasattr(active_amnt, 'get') else ''
    payee_val = active_payee.get() if active_payee and hasattr(active_payee, 'get') else ''
    mop_val = active_mop.get() if active_mop and hasattr(active_mop, 'get') else ''

    if not date_val or not desc_val or not amnt_val or not payee_val or not mop_val:
        if tb is not None:
            tb.showerror('Incomplete data', 'The data is incomplete, meaning fill all the fields first!')
        return False

    date_str = active_date.get_date() if hasattr(active_date, 'get_date') else date_val
    message = f'Your expense can be read like: \n"You paid {amnt_val} to {payee_val} for {desc_val} on {date_str} via {mop_val}"'

    add_question = True
    if tb is not None:
        add_question = tb.askyesno('Read your record like: ', f'{message}\n\nShould I add it to the database?')

    if add_question:
        add_another_expense(
            date_widget=active_date,
            payee_var=active_payee,
            desc_var=active_desc,
            amnt_var=active_amnt,
            mop_var=active_mop,
            conn=conn,
            tree=tree
        )
        return True
    else:
        if tb is not None:
            tb.showinfo('Ok', 'Please take your time to add this record')
        return False


def export_to_csv(conn=None, filepath=None):
    """Export the table data to a CSV file."""
    global connector
    active_conn = conn if conn is not None else connector

    if active_conn is None:
        data = []
    else:
        data = active_conn.execute('SELECT * FROM ExpenseTracker').fetchall()

    if not data:
        if tb is not None:
            tb.showerror("Export Failed", "No expenses to export!")
        return False

    save_file_path = filepath
    if not save_file_path and asksaveasfilename is not None:
        save_file_path = asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title="Save As"
        )

    if save_file_path:
        with open(save_file_path, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['ID', 'Date', 'Payee', 'Description', 'Amount', 'Mode of Payment'])
            writer.writerows(data)

        if tb is not None:
            tb.showinfo("Export Successful", f"Expenses exported to {save_file_path}")
        return True
    return False


def create_gui(conn, cur):
    """Construct and configure Tkinter GUI window, widgets, and layout.

    Args:
        conn (sqlite3.Connection): Database connection.
        cur (sqlite3.Cursor): Database cursor.

    Returns:
        dict: Dictionary containing references to instantiated GUI widgets and variables.
    """
    global root, table, Desc, amnt, payee, MoP, date, date_from, date_to, connector, cursor
    connector = conn
    cursor = cur

    if Tk is None:
        raise RuntimeError("Tkinter is not available in the current Python environment.")

    # Backgrounds and Fonts
    dataentery_frame_bg = 'light blue'
    buttons_frame_bg = 'tomato'
    hlb_btn_bg = 'Indianred'

    lbl_font = ('Georgia', 13)
    entry_font = 'Times 13 bold'
    btn_font = ('Gill Sans MT', 13)

    # Initializing the GUI window
    root = Tk()
    root.title('DebEx')
    root.geometry('1200x550')
    root.resizable(0, 0)

    Label(root, text='DebEx', font=('white', 21, 'bold'), bg=hlb_btn_bg).pack(side=TOP, fill=X)

    # StringVar and DoubleVar variables
    Desc = StringVar()
    amnt = DoubleVar()
    payee = StringVar()
    MoP = StringVar(value='Cash')

    # Frames
    data_entry_frame = Frame(root, bg=dataentery_frame_bg)
    data_entry_frame.place(x=0, y=35, relheight=0.95, relwidth=0.25)

    buttons_frame = Frame(root, bg=buttons_frame_bg)
    buttons_frame.place(relx=0.25, rely=0.063, relwidth=0.75, relheight=0.12)

    tree_frame = Frame(root)
    tree_frame.place(relx=0.25, rely=0.18, relwidth=0.75, relheight=0.8)

    # Data Entry Frame
    Label(data_entry_frame, text='Date (M/DD/YY) :', font=lbl_font, bg=dataentery_frame_bg).place(x=10, y=50)
    if DateEntry is not None:
        date = DateEntry(data_entry_frame, date=datetime.datetime.now().date(), font=entry_font)
    else:
        date = Entry(data_entry_frame, font=entry_font)
    date.place(x=160, y=50)

    Label(data_entry_frame, text='Payee\t             :', font=lbl_font, bg=dataentery_frame_bg).place(x=10, y=230)
    Entry(data_entry_frame, font=entry_font, width=31, text=payee).place(x=10, y=260)

    Label(data_entry_frame, text='Description           :', font=lbl_font, bg=dataentery_frame_bg).place(x=10, y=100)
    Entry(data_entry_frame, font=entry_font, width=31, text=Desc).place(x=10, y=130)

    Label(data_entry_frame, text='Amount\t             :', font=lbl_font, bg=dataentery_frame_bg).place(x=10, y=180)
    Entry(data_entry_frame, font=entry_font, width=14, text=amnt).place(x=160, y=180)

    Label(data_entry_frame, text='Mode of Payment:', font=lbl_font, bg=dataentery_frame_bg).place(x=10, y=310)
    dd1 = OptionMenu(data_entry_frame, MoP, *['Cash', 'Cheque', 'Credit Card', 'Debit Card', 'Paytm', 'Google Pay', 'Razorpay'])
    dd1.place(x=160, y=305)
    dd1.configure(width=10, font=entry_font)

    Button(data_entry_frame, text='Add expense', command=add_another_expense, font=btn_font, width=30,
           bg=hlb_btn_bg).place(x=10, y=395)

    # Buttons' Frame
    Button(buttons_frame, text='Delete Expense', font=btn_font, width=25, bg=hlb_btn_bg, command=remove_expense).place(x=30, y=5)
    Button(buttons_frame, text='Clear Fields in DataEntry Frame', font=btn_font, width=25, bg=hlb_btn_bg,
           command=clear_fields).place(x=335, y=5)
    Button(buttons_frame, text='Delete All Expenses', font=btn_font, width=25, bg=hlb_btn_bg, command=remove_all_expenses).place(x=640, y=5)

    # Filter Frame
    filter_frame = Frame(root, bg="light gray")
    filter_frame.place(x=10, y=500, width=1165, height=35)

    Label(filter_frame, text="Date From:", font=("Georgia", 10), bg="light gray").place(x=10, y=5)
    if DateEntry is not None:
        date_from = DateEntry(filter_frame, date=datetime.datetime.now().date(), width=10)
    else:
        date_from = Entry(filter_frame, width=10)
    date_from.place(x=90, y=5)

    Label(filter_frame, text="Date To:", font=("Georgia", 10), bg="light gray").place(x=200, y=5)
    if DateEntry is not None:
        date_to = DateEntry(filter_frame, date=datetime.datetime.now().date(), width=10)
    else:
        date_to = Entry(filter_frame, width=10)
    date_to.place(x=270, y=5)

    Button(filter_frame, text="Filter", font=('Gill Sans MT', 10), width=10, bg=hlb_btn_bg,
           command=lambda: filter_expenses_by_date(
               date_from.get_date() if hasattr(date_from, 'get_date') else date_from.get(),
               date_to.get_date() if hasattr(date_to, 'get_date') else date_to.get()
           )).place(x=400, y=3)

    Button(filter_frame, text="Export to CSV", font=('Gill Sans MT', 10), width=15, bg=hlb_btn_bg,
           command=export_to_csv).place(x=500, y=3)

    # Treeview Frame
    table = ttk.Treeview(tree_frame, selectmode=BROWSE, columns=('ID', 'Date', 'Payee', 'Description', 'Amount', 'Mode of Payment'))

    x_scroller = Scrollbar(table, orient=HORIZONTAL, command=table.xview)
    y_scroller = Scrollbar(table, orient=VERTICAL, command=table.yview)
    x_scroller.pack(side=BOTTOM, fill=X)
    y_scroller.pack(side=RIGHT, fill=Y)

    table.config(yscrollcommand=y_scroller.set, xscrollcommand=x_scroller.set)

    table.heading('ID', text='S No.', anchor=CENTER)
    table.heading('Date', text='Date', anchor=CENTER)
    table.heading('Payee', text='Payee', anchor=CENTER)
    table.heading('Description', text='Description', anchor=CENTER)
    table.heading('Amount', text='Amount', anchor=CENTER)
    table.heading('Mode of Payment', text='Mode of Payment', anchor=CENTER)

    table.column('#0', width=0, stretch=NO)
    table.column('#1', width=50, stretch=NO)
    table.column('#2', width=95, stretch=NO)
    table.column('#3', width=150, stretch=NO)
    table.column('#4', width=325, stretch=NO)
    table.column('#5', width=135, stretch=NO)
    table.column('#6', width=125, stretch=NO)

    table.place(relx=0, y=0, relheight=1, relwidth=1)

    # Populate initial table contents
    list_all_expenses(conn=connector, tree=table)

    return {
        "root": root,
        "table": table,
        "Desc": Desc,
        "amnt": amnt,
        "payee": payee,
        "MoP": MoP,
        "date": date,
        "date_from": date_from,
        "date_to": date_to,
    }


def main():
    """Main application entry point."""
    global connector, cursor
    connector, cursor = init_db("Expense Tracker.db")
    components = create_gui(connector, cursor)
    components["root"].update()
    components["root"].mainloop()


if __name__ == '__main__':
    main()
