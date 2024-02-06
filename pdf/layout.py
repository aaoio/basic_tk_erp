from fpdf import FPDF
from fpdf.enums import XPos, YPos, VAlign
from fpdf.fonts import FontFace
import pandas as pd

class PDF(FPDF):
    def __init__(self, orientation, unit, page_format, metadata):
        super().__init__(orientation, unit, page_format)
        self.metadata = metadata
        self.set_margins(20, 20, -20)

    def header(self):
        # company details
        self.image('pdf/logo.png', 20, 20, 15)
        self.set_font('Helvetica', 'B', 15)
        self.x = 36
        self.cell(0, 6, self.metadata['company'], new_x=XPos.LEFT,
                  new_y=YPos.NEXT, align='L', border=0)
        self.set_font('Helvetica', size=12)
        self.multi_cell(0, 5,
            self.metadata['email']+'\n'+self.metadata['telephone']
        )

        # document details
        if self.metadata['document_type'] == 'Quotation':
            self.set_font('Helvetica', size=36)
        elif self.metadata['document_type'] == 'Request for Quotation':
            self.set_font('Helvetica', size=24)
        self.y = 20
        self.set_x(-(
            self.get_string_width(self.metadata['document_type']
        ) + 20))
        self.cell(0, 10, self.metadata['document_type'], align='L',
                  new_x=XPos.LMARGIN,new_y=YPos.NEXT, border=0)
        self.set_font('Helvetica', size=12)
        self.set_x(-(self.get_string_width(
            self.metadata['document_number']
        )+20))
        self.cell(0, 4, self.metadata['document_number'], align='L',
                  new_x=XPos.LMARGIN, new_y=YPos.NEXT, border=0)
        self.set_x(-(
            self.get_string_width(self.metadata['document_date']
        )+20))
        self.cell(0, 4, self.metadata['document_date'], align='L',
                  new_x=XPos.LMARGIN, new_y=YPos.NEXT, border=0)
        self.set_x(-(
            self.get_string_width(self.metadata['customer_reference']
        )+20))
        if self.metadata['document_type'] == 'Quotation':
            self.cell(0, 4, self.metadata['customer_reference'],
                align='L', new_x=XPos.LMARGIN, new_y=YPos.NEXT, border=0)
        self.ln(3)
    
    def footer(self):
        self.y = 260
        self.x = 130
        self.cell(0, 10, f"Page {self.page_no()} of {{nb}}", align="C")


class DocumentPDF():
    def __init__(self, metadata, data):
        self.metadata = metadata
        self.data = data
        self.pdf = PDF('P', 'mm', 'A4', self.metadata)
        self.transform()
        self.body()
    
    def transform(self):
        if self.metadata['document_type'] == 'Quotation':
            self.data['description'] = (
                self.data['type'] + ', '
                + self.data['product_number'] + ', '
                + self.data['brand'] + '\n'
                + self.data['customer_description'] + '\n'
                + self.data['additional_notes']
            )
            self.data['amount'] = (
                self.data['cost'] * self.data['quantity']
            )
            self.data['quantity'] = self.data['quantity'].apply(lambda x: f'{x:,}')
            self.data[['cost', 'amount']] = self.data[['cost', 'amount']].applymap(lambda x: f'{round(x, 2):,}')
            self.data = self.data.applymap(lambda x: f'{x}\n\n')
            self.data['#'] = self.data.index + 1
            self.data = self.data[[
                '#', 'description', 'quantity', 'unit',
                'cost', 'amount', 'availability'
            ]]
            self.data.columns = [
                '#',
                'Description',
                'Qty',
                'Unit',
                'Unit price',
                'Amount',
                'Availability'
            ]
            self.data = pd.concat(
                (self.data.columns.to_frame().T, self.data),
                ignore_index=True
            )
        elif self.metadata['document_type'] == 'Request for Quotation':
            self.data['description'] = (
                self.data['type'] + ', '
                + self.data['product_number'] + ', '
                + self.data['brand']
            )
            self.data['quantity'] = self.data['quantity'].apply(lambda x: f'{x:,}')
            self.data = self.data.applymap(lambda x: f'{x}\n\n')
            self.data['#'] = self.data.index + 1
            self.data = self.data[[
                '#', 'description', 'quantity', 'unit'
            ]]
            self.data.columns = [
                '#',
                'Description',
                'Qty',
                'Unit'
            ]
            self.data = pd.concat(
                (self.data.columns.to_frame().T, self.data),
                ignore_index=True
            )


    def body(self):
        self.pdf.add_page()

        # address
        self.pdf.set_font('Helvetica', size=10)
        self.pdf.multi_cell(0, 4, self.metadata['address'],
                            align='L', border=0)
        self.pdf.ln(5)

        # recipient_details
        self.pdf.set_font('Helvetica', 'B', 10)
        self.pdf.cell(0, 4, self.metadata['recipient'],
            new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='L')
        self.pdf.set_font('Helvetica', size=10)
        self.pdf.multi_cell(0, 4, self.metadata['recipient_address'], 
            new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='L', border=0)
        self.pdf.ln(5)
    
        # table
        if self.metadata['document_type'] == 'Quotation':
            column_widths = [6, 79, 8, 9, 21, 21, 26]
            column_alignments = [
                'CENTER',
                'LEFT',
                'RIGHT',
                'LEFT',
                'RIGHT',
                'RIGHT',
                'LEFT']
            headings_style = FontFace(
                fill_color=(192, 192, 192)
            )
        elif self.metadata['document_type'] == 'Request for Quotation':
            column_widths = [6, 146, 8, 10]
            column_alignments = [
                'CENTER',
                'LEFT',
                'RIGHT',
                'LEFT']
            headings_style = FontFace(
                fill_color=(192, 192, 192)
            )

        with self.pdf.table(
            width=170,
            col_widths=column_widths,
            borders_layout='SINGLE_TOP_LINE',
            text_align=column_alignments,
            line_height=self.pdf.font_size + 1,
            padding=[1, 0],
            v_align=VAlign.T,
            headings_style=headings_style
        ) as table:
            for i, data_row in self.data.iterrows():
                row = table.row()
                for datum in data_row:
                    row.cell(str(datum))

    def create_pdf(self):
        self.pdf.output(f'output/{self.metadata["document_number"]}.pdf')
