from tkinter import ttk, messagebox
import locale
import controller.sales as sales
from view.document_editor import (DocumentEditorData,
    DocumentEditorLeftFrame, DocumentEditorRightFrame)

class QuotationEditor(ttk.Frame):
    def __init__(self, parent, session):
        super().__init__(parent)
        self.session = session
        locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
        self.data = DocumentEditorData(self.session)
        self.left_frame = QuotationEditorLeftFrame(
            self,
            self.session,
            self.data
        )
        self.right_frame = QuotationEditorRightFrame(
            self,
            self.session,
            self.data
        )
        self.layout()

    def layout(self):
        self.columnconfigure((0, 1), weight=1, uniform='a')
        self.rowconfigure(0, weight=1)
        self.left_frame.grid(row=0, column=0, sticky='news',
                             padx=20, pady=20)
        self.right_frame.grid(row=0, column=1, sticky='news',
                              padx=20, pady=20)

class QuotationEditorLeftFrame(DocumentEditorLeftFrame):
    def __init__(self, parent, session, data):
        super().__init__(parent, session, data)
        self.add_button = ttk.Button(
            self,
            text='Add to quotation',
            command=lambda: self.add_to_document()
        )
        self.layout()

class QuotationEditorRightFrame(DocumentEditorRightFrame):    
    def __init__(self, parent, session, data):
        super().__init__(parent, session, data)
        self.save_document_button = ttk.Button(
            self,
            text='Save quotation',
            command=lambda: self.save_document()
        )
        self.layout()
    
    def save_document(self):
        if not self.data.document_df.empty:
            if self.data.customer_var.get():
                customer_pk = self.data.customers_df[
                    self.data.customers_df[
                        'company_name'
                    ]==self.data.customer_var.get()
                ]['company_pk'].values[0]
                sales.create_quotation(
                    self.session,
                    self.data.document_df,
                    customer_pk=customer_pk,
                    rfq_number=self.data.rfq_number_var.get(),
                    rfq_date=self.rfq_date_entry.get_date()
                )
                self.data.document_df.drop(
                    self.data.document_df.index,
                    inplace=True
                )
                self.update_document_table()
                self.parent.left_frame.toggle_new_entry_checkbutton()
            else:
                messagebox.showerror('','No customer selected.')
        else:
            messagebox.showerror('', 'Quotation is empty.')