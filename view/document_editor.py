import locale
import tkinter as tk
from tkinter import ttk
import tkcalendar as tkc
import pandas as pd
from controller import sales

class DocumentEditorLeftFrame(ttk.Frame):
    def __init__(self, parent, session, data):
        super().__init__(parent)
        self.parent = parent
        self.data = data
        self.session = session
        self.set_grid()

        # WIDGETS
        self.results_table = self.create_results_table()
        self.customer_description_entry = tk.Text(self)
        self.additional_notes_entry = tk.Text(self)
        self.new_entry_checkbutton = ttk.Checkbutton(
            self,
            text='Add as a separate entry',
            variable=self.data.new_entry_var,
        )
        self.search_bar = ttk.Entry(
            self,
            textvariable=self.data.search_var
        )
        self.search_button = ttk.Button(
            self,
            text='Search products list',
            command=lambda: self.search(
                self.data.search_var.get()
            )
        )
        self.customer_description_label = ttk.Label(
            self,
            text='Customer description:'
        )
        self.additional_notes_label = ttk.Label(
            self,
            text='Additional notes:'
        )
        self.pricing_label = ttk.Label(self, text='Price:')
        self.last_price_radio = ttk.Radiobutton(
            self,
            value='last_price',
            variable=self.data.price_radio_var,
            text='Use most recent price:'
        )
        self.last_price_label = ttk.Label(
            self,
            textvariable=self.data.last_price_var
        )
        self.price_entry_radio = ttk.Radiobutton(
            self,
            value='price_entry',
            variable=self.data.price_radio_var,
            text='Use another price:'
        )
        self.price_entry = ttk.Entry(
            self,
            textvariable=self.data.price_entry_var
        )
        self.availability_label = ttk.Label(self,text='Availability:')
        self.availability_entry = ttk.Entry(
            self,
            textvariable=self.data.availability_var
        )
        self.quantity_bar = ttk.Spinbox(
            self,
            from_=1,
            to=5000,
            increment=1,
            textvariable=self.data.quantity_var
        )
        self.quantity_label = ttk.Label(
            self,
            text='Quantity:'
        )
        self.unit_label = ttk.Label(
            self,
            textvariable=self.data.unit_var
        )
        self.add_button = ttk.Button(
            self,
            text='Add to document',
            command=lambda: self.parent.add_to_document()
        )
        self.bind_keys()
    
    def set_grid(self):
        self.columnconfigure(
            (0, 1, 2, 3),
            weight=1,
            uniform='a'
        )
        self.rowconfigure(
            (0, 3, 4, 9),
            weight=1,
            uniform='a'
        )
        self.rowconfigure(
            (1, 2),
            weight=3,
            uniform='a'
        )

    def create_results_table(self):
        results_table = ttk.Treeview(
            self,
            columns=(
                'supplier',
                'description',
                'unit_cost',
                'net_unit_cost'
            ),
            show='headings'
        )
        results_table.heading('supplier', text='Supplier')
        results_table.heading('description', text='Description')
        results_table.heading('unit_cost', text='Unit Cost')
        results_table.heading('net_unit_cost', text='Net Unit Cost')

        results_table.column('supplier', minwidth=0, width=60)
        results_table.column('description', minwidth=0, width=300)
        results_table.column('unit_cost', minwidth=0, width=90)
        results_table.column('net_unit_cost', minwidth=0, width=90)

        return results_table

    def bind_keys(self):
        # self.search_bar.bind('<Enter>', self.search)
        self.results_table.bind(
            '<<TreeviewSelect>>',
            self.results_table_select
        )

    def layout(self):
        self.search_bar.grid(row=0, column=0,
            columnspan=3, rowspan=1, sticky='ew', padx=4, pady=4)
        self.search_button.grid(row=0, column=3,
            columnspan=1, rowspan=1, sticky='ew', padx=4, pady=4)
        self.results_table.grid(row=1, column=0,
            columnspan=4, rowspan=2, sticky='news', padx=4, pady=4)
        self.customer_description_label.grid(row=3, column=0,
            columnspan=1, rowspan=1, sticky='e', padx=0, pady=0)
        self.customer_description_entry.grid(row=3, column=1,
            columnspan=3, rowspan=1, sticky='news', padx=4, pady=4)
        self.additional_notes_label.grid(row=4, column=0, 
            columnspan=1, rowspan=1, sticky='e', padx=0, pady=0)
        self.additional_notes_entry.grid(row=4, column=1,
            columnspan=3, rowspan=1, sticky='news', padx=4, pady=0)
        self.availability_label.grid(row=5, column=0,
            columnspan=1, rowspan=1, sticky='e', padx=4, pady=4)
        self.availability_entry.grid(row=5, column=1,
            columnspan=3, rowspan=1, sticky='ew', padx=4, pady=4)
        self.pricing_label.grid(row=6, column=0,
            columnspan=1, rowspan=2, sticky='e', padx=4, pady=4)
        self.last_price_radio.grid(row=6, column=1,
            columnspan=1, rowspan=1, sticky='w', padx=4, pady=4)
        self.last_price_label.grid(row=6, column=2,
            columnspan=1, rowspan=1, sticky='w', padx=0, pady=0)
        self.price_entry_radio.grid(row=7, column=1,
            columnspan=1, rowspan=1, sticky='w', padx=4, pady=4)
        self.price_entry.grid(row=7, column=2,
            columnspan=1, rowspan=1, sticky='w', padx=0, pady=0)
        self.quantity_label.grid(row=8, column=0,
            columnspan=1, rowspan=1, sticky='e', padx=4, pady=0)
        self.quantity_bar.grid(row=8, column=1,
            columnspan=1, rowspan=1, sticky='e', padx=4, pady=4)
        self.unit_label.grid(row=8, column=2,
            columnspan=1, rowspan=1, sticky='w', padx=0, pady=0)
        self.add_button.grid(row=9, column=0,
            columnspan=4, rowspan=1, sticky='news', padx=4, pady=10)

    def search(self, event):
        self.data.results_df.drop(
            self.data.results_df.index, inplace=True
        )
        if self.data.search_var.get():
            results_list = sales.search_supplier_products(
                    self.session,
                    self.data.search_var.get()
                )
            results_data = []
            for i in results_list:
                costs = i.supplier_product_cost
                current_cost = [
                    c for c in costs if c.is_current is True
                ][0]
                last_price = sales.get_last_price(self.session, i)
                results_data.append([
                        i.pk,
                        i.product.unit_of_measure,
                        i.company.company_code,
                        i.product.product_type,
                        i.product.brand,
                        i.product.product_number,
                        current_cost.currency,
                        current_cost.cost,
                        current_cost.discount,
                        current_cost.calculated_price,
                        last_price
                ])
            self.data.results_df = pd.concat(
                [self.data.results_df, pd.DataFrame(
                    results_data,
                    columns=self.data.results_df.columns
                )],
                ignore_index=True
            )
        self.update_results_table()

    def results_table_select(self, event):
        self.get_unit()
        self.toggle_new_entry_checkbutton()
        self.get_calculated_price()
        self.get_last_price()

    def update_results_table(self):
        self.results_table.delete(*self.results_table.get_children())
        for i, r in self.data.results_df.iterrows():
            unit_cost = f'{r["currency"]} {r["cost"]:,.2f}'
            discount = f'-{r["discount"]*100:,.2f}%'
            net_unit_cost = f'{r["currency"]} {r["cost"]*(1-r["discount"]):,.2f}'
            self.results_table.insert(
                parent='',
                index=i,
                values=(
                    r['supplier'],
                    f'{r["type"]}\n{r["brand"]}\n{r["product_number"]}',
                    f'{unit_cost}\n({discount})',
                    net_unit_cost
                )
            )

    def get_unit(self):
        if len(self.results_table.selection()) == 1:
            selection = self.results_table.selection()[0]
            selection_index = self.results_table.index(selection)
            unit = self.data.results_df.iloc[selection_index]['unit']
            self.data.unit_var.set(f'{unit}s'.lower())
    
    def get_calculated_price(self):
        if len(self.results_table.selection()) == 1:
            selection = self.results_table.selection()[0]
            selection_index = self.results_table.index(selection)
            calculated_price = self.data.results_df.iloc[selection_index]['calculated_price']
            self.data.price_entry_var.set(f'{calculated_price:,.2f}')
    
    def get_last_price(self):
        if len(self.results_table.selection()) == 1:
            selection = self.results_table.selection()[0]
            selection_index = self.results_table.index(selection)
            last_price = self.data.results_df.iloc[selection_index]['last_price']
            if last_price:
                self.last_price_radio['state'] = 'enabled'
                self.data.price_radio_var.set('last_price')
                self.data.last_price_var.set(f'{last_price:,.2f}')
            else:
                self.data.price_radio_var.set('price_entry')
                self.last_price_radio['state'] = 'disabled'
                self.data.last_price_var.set('-')

    def toggle_new_entry_checkbutton(self):
        self.data.new_entry_var.set(0)

        if self.data.new_entry_checkbutton_visible:
            self.new_entry_checkbutton.grid_forget()
            self.data.new_entry_checkbutton_visible = False

        if len(self.results_table.selection()) == 1:
            selection = self.results_table.selection()[0]
            selection_index = self.results_table.index(selection)
            selected_item = self.data.results_df.iloc[selection_index]
            added_items = self.data.document_df['supplier_product_pk']
            row_match = added_items.isin(
                [selected_item.loc['supplier_product_pk']]
            )

            if row_match.any():
                self.new_entry_checkbutton.grid(row=6, column=3,
                    columnspan=1, rowspan=1, sticky='e', padx=4, pady=0)
                self.data.new_entry_checkbutton_visible = True

    def add_to_document(self):
        quantity = self.data.quantity_var.get()
        availability = self.data.availability_var.get()
        if self.data.price_radio_var.get() == 'last_price':
            unit_price = locale.atof(self.data.last_price_var.get())
        elif self.data.price_radio_var.get() == 'price_entry':
            unit_price = locale.atof(self.data.price_entry_var.get())
        if len(self.results_table.selection()) == 1:
            selection = self.results_table.selection()[0]
            selection_index = self.results_table.index(selection)
            selected_item = self.data.results_df.iloc[selection_index]

            customer_description = self.customer_description_entry.get(
                1.0,'end-1c'
            )
            additional_notes = self.additional_notes_entry.get(
                1.0,'end-1c'
            )

            added_items = self.data.document_df['supplier_product_pk']
            row_match = added_items.isin(
                [selected_item.loc['supplier_product_pk']]
            )
            if row_match.any() and self.data.new_entry_var.get() is False:
                last_added = max(row_match.index)
                self.data.document_df.loc[last_added,
                    'quantity'] += quantity
                self.data.document_df.loc[last_added,
                    'customer_description'] = customer_description
                self.data.document_df.loc[last_added,
                    'additional_notes'] = additional_notes
                self.data.document_df.loc[last_added,
                    'unit_price'] = unit_price
                self.data.document_df.loc[last_added,
                    'availability'] = availability
            else:
                row = pd.concat([
                    pd.Series({
                        'quantity': quantity,
                        'customer_description': customer_description,
                        'additional_notes': additional_notes,
                        'unit_price': unit_price,
                        'availability': availability
                    }),
                    selected_item
                ])
                self.data.document_df = pd.concat(
                    (self.data.document_df, row.to_frame().T),
                    ignore_index=True
                )

            self.customer_description_entry.delete(1.0,'end-1c')
            self.additional_notes_entry.delete(1.0,'end-1c')
            self.data.availability_var.set(
                'Ex stock, subject to prior sale.'
            )

        self.toggle_new_entry_checkbutton()
        self.parent.right_frame.update_document_table()

class DocumentEditorRightFrame(ttk.Frame):
    def __init__(self, parent, session, data):
        super().__init__(parent)
        self.parent = parent
        self.data = data
        self.session = session
        self.set_grid()

        # WIDGETS
        self.document_table = self.create_document_table()
        self.rfq_number_label = ttk.Label(self, text='RFQ no.:')
        self.rfq_number_entry = ttk.Entry(self, textvariable=self.data.rfq_number_var)
        self.rfq_date_label = ttk.Label(self, text='RFQ Date:')
        self.rfq_date_entry = tkc.DateEntry(
            self,
            width=12,
            borderwidth=2,
            date_pattern='dd-M-y'
        )
        self.save_document_button = ttk.Button(
            self,
            text='Save document',
            command=lambda: self.save_document()
        )
        self.customer_menu_label = ttk.Label(self, text='Customer:')
        self.customer_menu = tk.OptionMenu(
            self,
            self.data.customer_var,
            *[i for i in self.data.customers_df[
                'company_name'
            ].to_list()]
        )
        self.bind_keys()


    def set_grid(self):
        self.columnconfigure(
            (0,1,2,3,4,5,6,7,8,9),
            weight=1,
            uniform='a'
        )
        self.rowconfigure(
            (0, 3, 6),
            weight=1,
            uniform='a'
        )
        self.rowconfigure(
            (1, 2),
            weight=3,
            uniform='a'
        )

    def create_document_table(self):
        document_table = ttk.Treeview(
            self,
            columns=(
                'quantity',
                'supplier',
                'description',
                'unit_cost',
                'net_unit_cost',
                'unit_price',
                'availability'
            ),
            show='headings'
        )
        document_table.heading('quantity', text='Qty')
        document_table.heading('supplier', text='Supplier')
        document_table.heading('description', text='Description')
        document_table.heading('unit_cost', text='Unit Cost')
        document_table.heading('net_unit_cost', text='Net Unit Cost')
        document_table.heading('unit_price', text='Unit Price')
        document_table.heading('availability', text='Availability')

        document_table.column('quantity', minwidth=0, width=40)
        document_table.column('supplier', minwidth=0, width=60)
        document_table.column('description', minwidth=0, width=250)
        document_table.column('unit_cost', minwidth=0, width=123)
        document_table.column('net_unit_cost', minwidth=0, width=123)
        document_table.column('unit_price', minwidth=0, width=123)
        document_table.column('availability', minwidth=0, width=110)

        return document_table

    def bind_keys(self):
        self.document_table.bind('<Delete>', self.remove_from_document)

    def layout(self):
        self.document_table.grid(row=0, column=0,
            columnspan=10, rowspan=4, sticky='news', padx=4, pady=4)
        self.customer_menu_label.grid(row=5, column=0,
            columnspan=1, rowspan=1, sticky='nws', padx=4, pady=0)
        self.customer_menu.grid(row=5, column=1,
            columnspan=3, rowspan=1, sticky='news', padx=4, pady=0)
        self.rfq_number_label.grid(row=5, column=4,
            columnspan=1, rowspan=1, sticky='e', padx=4, pady=4)
        self.rfq_number_entry.grid(row=5, column=5,
            columnspan=2, rowspan=1, sticky='news', padx=4, pady=4)
        self.rfq_date_label.grid(row=5, column=7,
            columnspan=1, rowspan=1, sticky='e', padx=4, pady=4)
        self.rfq_date_entry.grid(row=5, column=8,
            columnspan=2, rowspan=1, sticky='news', padx=4, pady=4)
        self.save_document_button.grid(row=6, column=0,
            columnspan=10, rowspan=1, sticky='news', padx=4, pady=10)

    def remove_from_document(self, event):
        if self.document_table.selection():
            for i in self.document_table.selection():
                selection_index = self.document_table.index(i)
                self.data.document_df.drop(selection_index, inplace=True)
        self.data.document_df.reset_index(inplace=True, drop=True)
        self.update_document_table()

    def save_document(self):
        pass

    def update_document_table(self):
        self.document_table.delete(
            *self.document_table.get_children()
        )
        for i, r in self.data.document_df.iterrows():
            desc_1 = f'{r["type"]}, {r["brand"]}, {r["product_number"]}'
            desc_2 = r["customer_description"]
            desc_3 = r["additional_notes"]
            unit_cost = f'{r["currency"]} {r["cost"]:,.2f}'
            discount = f'-{r["discount"]*100:,.2f}%'
            net_unit_cost = f'{r["currency"]} {r["cost"]*(1-r["discount"]):,.2f}'
            self.document_table.insert(
                parent='',
                index=i,
                values=(
                    f'{r["quantity"]}\n{r["unit"].lower()}s',
                    r['supplier'],
                    f'{desc_1}\n{desc_2}\n{desc_3}',
                    f'{unit_cost}\n({discount})',
                    net_unit_cost,
                    f'PHP {r["unit_price"]:,.2f}',
                    r['availability']
                )
            )

class DocumentEditorData():
    '''
    Handle shared data between Tkinter objects
    in the DocumentEditor frame.
    '''
    def __init__(self, session):
        self.session = session
        # dataframes
        self.results_df, self.document_df = self.create_dfs()
        self.customers_df = pd.DataFrame(
            [[i.pk, i.company_name] for i in sales.search_companies(
                self.session)],
            columns=['company_pk', 'company_name']
        )

        # tkinter variables
        self.unit_var = tk.StringVar()
        self.search_var = tk.StringVar()
        self.quantity_var = tk.IntVar(value=1)
        self.new_entry_var = tk.BooleanVar(value=0)
        self.customer_var = tk.StringVar()
        self.price_entry_var = tk.StringVar()
        self.last_price_var = tk.StringVar()
        self.price_radio_var = tk.StringVar(value='last_price')
        self.availability_var = tk.StringVar(
            value='Ex stock, subject to prior sale.'
        )
        self.rfq_number_var = tk.StringVar()

        # python variables
        self.new_entry_checkbutton_visible = False

    def create_dfs(self):
        results_df = pd.DataFrame(
            columns=[
                'supplier_product_pk',
                'unit',
                'supplier',
                'type',
                'brand',
                'product_number',
                'currency',
                'cost',
                'discount',
                'calculated_price',
                'last_price'
            ]
        )
        document_df = pd.DataFrame(
            columns=[
                'supplier_product_pk',
                'quantity',
                'unit',
                'supplier',
                'type',
                'brand',
                'product_number',
                'currency',
                'cost',
                'discount',
                'unit_price',
                'customer_description',
                'additional_notes',
                'availability'
            ]            
        )
        return results_df, document_df