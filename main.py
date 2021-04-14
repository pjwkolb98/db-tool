import tkinter as tk
from tkinter import ttk
from tkinter import font as tkfont
import mysql.connector as connector

global current_connection
global current_database
global current_table
global current_action


class App(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self._frame = None
        self.switch_frame(DBChoicePage)
        self.title_font = tkfont.Font(family='Helvetica', size=18, weight='bold')
        self.title('DBTool')
        self.iconbitmap('eyec.ico')
        self.geometry('1000x600')

    def switch_frame(self, frame_class):
        new_frame = frame_class(self)
        if self._frame is not None:
            self._frame.destroy()
        self._frame = new_frame
        self._frame.pack()


class DBChoicePage(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        label = tk.Label(self, text='Databases:', font=tkfont.Font(family='Helvetica', size=18, weight='bold'))
        label.pack(side='top', fill='x', pady=10)

        conn = connect_with_db(db_name=None)
        dbs = get_databases(conn)
        for db in dbs:
            button = tk.Button(self, text=db,
                               command=lambda db_arg=db: [set_current_db(db_arg), master.switch_frame(TableChoicePage)])
            button.pack(pady=10)


class TableChoicePage(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        back_button = tk.Button(self, text='back',
                                command=lambda: master.switch_frame(DBChoicePage))
        back_button.pack(pady=10)

        label = tk.Label(self, text=f'Database: {current_database}\n\nKies tabel:',
                         font=tkfont.Font(family='Helvetica', size=18, weight='bold'))
        label.pack(side='top', fill='x', pady=10)

        for table in get_tables(current_connection):
            button = tk.Button(self, text=table,
                               command=lambda tab_arg=table: [set_current_table(tab_arg),
                                                              master.switch_frame(TablePage)])
            button.pack(pady=10)


class TablePage(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        label = tk.Label(self, text=f'Tabel: {current_table}',
                         font=tkfont.Font(family='Helvetica', size=18, weight='bold'))
        label.pack(side='top', pady=10)
        # label.grid(row=0, columnspan=2, ipady=20)

        back_button = tk.Button(self, text='back',
                                command=lambda: master.switch_frame(TableChoicePage))
        back_button.pack(side='top')
        # back_button.grid(row=0, column=1)
        columns = tuple(get_columns(current_connection, current_table))

        tree_frame = tk.Frame(self, width=850, height=550)
        tree_frame.pack(side='left', expand=True, fill='both')
        tree_frame.pack_propagate(0)
        # tree_frame.grid(row=1, column=0)

        # TODO - set scrollbar to treeview frame
        hor_scrollbar = tk.Scrollbar(tree_frame, orient='horizontal')
        hor_scrollbar.pack(side='bottom', fill='x')

        ver_scrollbar = tk.Scrollbar(tree_frame, orient='vertical')
        ver_scrollbar.pack(side='right', fill='y')

        treeview = ttk.Treeview(tree_frame, height=23,
                                xscrollcommand=hor_scrollbar.set, yscrollcommand=ver_scrollbar.set)
        treeview['columns'] = columns
        treeview['show'] = 'headings'

        for i in range(0, len(columns)):
            treeview.column(columns[i], width=150)
            treeview.heading(columns[i], text=columns[i])
        treeview.pack(padx=10, expand=True)
        # treeview.grid(row=1, column=0, padx=20)

        hor_scrollbar.config(command=treeview.xview)
        ver_scrollbar.config(command=treeview.yview)

        rows = select(current_table)
        count = 0
        for row in rows:
            treeview.insert(parent='', index='end', iid=count, values=row)
            count += 1

        # TODO - functionality for buttons
        button_frame = tk.Frame(self)
        # button_frame.grid(row=1, column=1)
        button_frame.pack(side='right')

        # select_rows = tk.Button(button_frame, text='select more',
        #                         command=lambda action_arg='SELECT': [set_current_action(action_arg), master.switch_frame(InputPage)]) TODO - if select limit rows implemented, add button for extra rows
        # select_rows.grid(row=0, column=0, pady=10)

        insert = tk.Button(button_frame, text='insert',
                           command=lambda action_arg='INSERT': [set_current_action(action_arg),
                                                                master.switch_frame(InsertPage)])
        insert.grid(row=0, column=0, pady=10)

        update = tk.Button(button_frame, text='update',
                           command=lambda action_arg='UPDATE': [set_current_action(action_arg),
                                                                master.switch_frame(InsertPage)])
        update.grid(row=1, column=0, pady=10)

        delete = tk.Button(button_frame, text='delete',
                           command=lambda action_arg='DELETE': [set_current_action(action_arg), master.switch_frame(
                               InsertPage)])  # TODO - change to conformation screen (wilt u dit verwijderen?;records)
        delete.grid(row=2, column=0, pady=10)


class InsertPage(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        label = tk.Label(self, text=f'INSERT in tabel: {current_table}',
                         font=tkfont.Font(family='Helvetica', size=18, weight='bold'))
        label.grid(row=0, column=2, columnspan=2, ipady=20)

        back_button = tk.Button(self, text='back',
                                command=lambda: master.switch_frame(TablePage))
        back_button.grid(row=0, column=4, padx=20)
        count = 1
        columns = get_columns(current_connection, current_table)
        entries = []
        # entry_dict = {column_name: None for column_name in columns}
        for col_name in columns:
            label = tk.Label(self, text=f'{col_name}:')
            label.grid(row=count, column=1, ipady=5, pady=5)
            entry = tk.Entry(self, width=50)
            entry.grid(row=count, column=2, ipady=5, pady=5)
            entries.append(entry)
            count += 1
        complete_button = tk.Button(self, text='complete',
                                    command=lambda values_arg=entries, columns_arg=columns: [add_to_db(entries), master.switch_frame(TablePage)])  # TODO - add to db and switch frame
        complete_button.grid(row=count, column=2, pady=20)


def add_to_db(entries):
    values = []
    for entry in entries:
        value = entry.get()
        values.append(value)
    insert(current_table, values)


def insert(table, values):
    global current_connection
    cursor = current_connection.cursor()
    cursor.execute(f'INSERT INTO {table} VALUES {values};')  # TODO - change to insert into statement
    result = cursor.fetchall()
    return result


def select(table):
    global current_connection
    cursor = current_connection.cursor()
    cursor.execute(f'SELECT * FROM {table};')  # TODO - maybe limit rows
    result = cursor.fetchall()
    return result


def set_current_db(database):
    global current_database
    global current_connection
    current_database = database
    current_connection = connect_with_db(database)


def set_current_table(table):
    global current_table
    current_table = table


def set_current_action(action):
    global current_action
    current_action = action


def connect_with_db(db_name=None):
    # Functie om verbinding te maken met de host (of met database op de host)
    # param 'db_name': optionele parameter met naam van database
    # return 'conn': actieve verbinding
    if db_name is None:
        connection = connector.connect(
            host='localhost',
            user='admin',
            password='TheUltimateKey'
        )
    else:
        connection = connector.connect(
            host='localhost',
            user='admin',
            password='TheUltimateKey',
            database=db_name
        )
    return connection


def get_databases(connection):
    # Functie om lijst met databases op de host te genereren
    # param 'connection': actieve verbinding met host
    # return 'db_names': lijst met de namen van de databases op de host
    excluded_dbs = [('information_schema',), ('mysql',), ('performance_schema',), ('phpmyadmin',)]
    db_tuples = []
    cursor = connection.cursor()
    cursor.execute('SHOW DATABASES;')
    result = cursor.fetchall()

    for table in result:
        if table not in excluded_dbs:
            db_tuples.append(table)

    db_names = [db[0] for db in db_tuples]
    return db_names


def get_tables(connection):
    # Functie om lijst met tabellen in de database te genereren
    # param 'connection': actieve verbinding met een database op de host
    # return 'table_names': lijst met de namen van de tabellen in de database
    cursor = connection.cursor()
    cursor.execute('SHOW TABLES;')
    result = cursor.fetchall()

    table_names = [table[0] for table in result]
    return table_names


def get_columns(connection, table):
    # Functie om lijst met kolommen in de tabel te genereren
    # param 'connection': actieve verbinding met een database op de host
    # param 'table': de naam van de tabel in kwestie
    # return 'column_names': lijst met de namen van de kolommen in de tabel
    cursor = connection.cursor()
    cursor.execute(f'DESCRIBE {table};')
    result = cursor.fetchall()

    column_names = [column[0] for column in result]
    return column_names


"""
conn = connect_with_db()
databases = get_databases(conn)

conn = connect_with_db(databases[0])
tables = get_tables(conn)
columns = get_columns(conn, tables[0])
print(columns)
# TODO - for column_name in columns: maak frame met inputs
"""

app = App()
app.mainloop()  # Listener voor de app (events, clicks, keys)
