import tkinter as tk
from tkinter import font as tkfont


class App(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        self.title_font = tkfont.Font(family='Helvetica', size=18, weight='bold')
        self.title('DBTool')
        self.iconbitmap('eyec.ico')
        self.geometry('500x400')

        # the container is where we'll stack a bunch of frames
        # on top of each other, then the one we want visible
        # will be raised above the others
        container = tk.Frame(self)
        container.pack(side='top', fill='both', expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in (DBChoicePage, TableChoicePage, CRUDPage):
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame

            # put all of the pages in the same location;
            # the one on the top of the stacking order
            # will be the one that is visible.
            frame.grid(row=0, column=0, sticky='nsew')

        self.show_frame('DBChoicePage')

    def show_frame(self, page_name):
        # Show a frame for the given page name
        frame = self.frames[page_name]
        frame.tkraise()


class DBChoicePage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        label = tk.Label(self, text='DBChoicePage', font=controller.title_font)
        label.pack(side='top', fill='x', pady=10)

        # TODO - for db on host: make button and set curr db = db on click
        button1 = tk.Button(self, text='TableChoicePage',
                            command=lambda: ['set_db()', controller.show_frame('TableChoicePage')])
        button1.pack()


class TableChoicePage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        label = tk.Label(self, text='TableChoicePage', font=controller.title_font)
        label.pack(side='top', fill='x', pady=10)

        # TODO - for table in db: make button and set curr table = table on click
        button1 = tk.Button(self, text='CRUDPage',
                            command=lambda: ['set_table()', controller.show_frame('CRUDPage')])
        button1.pack()


class CRUDPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        label = tk.Label(self, text='CRUDPage', font=controller.title_font)
        label.pack(side='top', fill='x', pady=10)

        # TODO - treeview with first 50 rows and buttons for more rows(select), insert, update, deleter
        button1 = tk.Button(self, text='Treeview',
                            command=lambda: controller.show_frame('CRUDPage'))
        button1.pack()
