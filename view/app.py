import tkinter as tk
from tkinter import ttk

from view.tabs import QuotationEditor

class App(tk.Tk):
    def __init__(self, session):
        super().__init__()
    
        self.title('ERP')
        self.geometry('1920x1080')
        self.minsize(1366, 768)
        self.session = session
        ttk.Style().configure('Treeview', rowheight=60)

        QuotationEditor(self, self.session).pack(
            expand=True, fill='both'
        )