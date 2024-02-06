from datetime import datetime
import pandas as pd
from sqlalchemy import or_, select
from sqlalchemy.sql.expression import func
from configparser import ConfigParser

# from model.product_tables import *
from model.models import *
from pdf.layout import DocumentPDF

def search_supplier_products(session, search_string):
    '''
    Return a list of SupplierProduct objects.
    '''
    results = []
    statement = select(SupplierProduct).join(
        SupplierProduct.product
    ).where(
        Product.product_number.like(f'%{search_string}%')
    )
    results.extend(session.scalars(statement).all())
    return results

def search_companies(session):
    '''
    Return a list of all companies in the database.
    '''
    companies = session.query(Company).all()
    return companies

def get_last_price(session, supplier_product):
    '''
    Return a product's last quoted price.
    '''
    results = []
    statement = select(QuotationLineitem).join(
        QuotationLineitem.supplier_product
    ).join(
        SupplierProduct.product
    ).where(
        (Product.pk.like(supplier_product.product.pk))
    )
    results.extend(session.scalars(statement).all())
    if len(results) >= 1:
        latest = max(results, key=lambda x: x.quotation.date_issued)
        return latest.unit_price
    else:
        return None


def next_quotation_number(session):
    '''
    Return the next sequence number for quotations.
    '''
    sq = session.query(func.max(Quotation.pk)).scalar()
    last_number = session.query(
        Quotation.quotation_number
    ).filter(Quotation.pk==sq).scalar()
    next_number = int(last_number) + 1
    next_number_str = str(next_number).zfill(5)
    return next_number_str

def create_quotation(session, data, customer_pk, rfq_number, rfq_date):
    '''
    Create a Quotation object and a quotation PDF document.
    '''
    config = ConfigParser()
    config.read('company_info.ini')
    company_info = config['DEFAULT']
    customer = session.query(Company).filter_by(
        pk=int(customer_pk)
    ).first()

    # Quotation object
    quotation_lineitem = []
    for index, row in data.iterrows():
        line = QuotationLineitem(
            fk_supplier_product=row['supplier_product_pk'],
            customer_description=row['customer_description'],
            additional_notes=row['additional_notes'],
            quoted_quantity=row['quantity'],
            unit_price=row['unit_price'],
            availability=row['availability']
        )
        quotation_lineitem.append(line)
    
    quotation = Quotation(
        fk_company=customer.pk,
        quotation_number=next_quotation_number(session),
        date_issued=datetime.today(),
        rfq_number=rfq_number,
        rfq_date=rfq_date,
        quotation_lineitem=quotation_lineitem
    )
    session.add(quotation)
    session.commit()
    
    # Quotation PDF

    metadata = {
        'company': company_info['company'],
        'address': company_info['address'],
        'telephone': company_info['telephone'],
        'email': company_info['email'],
        'recipient': customer.company_name,
        'recipient_address': customer.address,
        'customer_reference': rfq_number,
        'document_type': 'Quotation',
        'document_number': quotation.quotation_number,
        'document_date': datetime.today().strftime('%Y-%m-%d')
    }
    quotation_pdf = DocumentPDF(metadata, data)
    quotation_pdf.create_pdf()

