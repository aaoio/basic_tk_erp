from datetime import date, datetime
from typing import List, Optional

from sqlalchemy import (ForeignKey, SmallInteger, String, Numeric)
from sqlalchemy.orm import (DeclarativeBase, Mapped, mapped_column,
                            relationship)

class Base(DeclarativeBase):
    pass

class Company(Base):
    __tablename__ = 'company'
    pk: Mapped[int] = mapped_column(primary_key=True)
    company_name: Mapped[str] = mapped_column(String(99),nullable=False)
    company_code: Mapped[str] = mapped_column(String(10),nullable=False)
    tin: Mapped[int] = mapped_column(nullable=False)
    address: Mapped[str] = mapped_column(nullable=False)
    city: Mapped[str] = mapped_column(String(50), nullable=False)
    zip_code: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    province: Mapped[str] = mapped_column(String(50), nullable=False)
    country: Mapped[str] = mapped_column(String(50), nullable=False)
    company_delivery_address: Mapped[List['CompanyDeliveryAddress']] = \
        relationship(back_populates='company')
    supplier_product: Mapped[List['SupplierProduct']] = relationship(
        back_populates='company'
    )
    quotation: Mapped[List['Quotation']] = relationship(
        back_populates='company'
    )
    purchase_order: Mapped[List['PurchaseOrder']] = relationship(
        back_populates='company'
    )

class CompanyDeliveryAddress(Base):
    __tablename__ = 'company_delivery_address'
    pk: Mapped[int] = mapped_column(primary_key=True)
    fk_company: Mapped[int] = mapped_column(
        ForeignKey('company.pk'),
        nullable=False
    )
    address: Mapped[str] = mapped_column(nullable=False)
    company: Mapped['Company'] = relationship(
        back_populates='company_delivery_address'
    )
    sales_order: Mapped[List['SalesOrder']] = relationship(
        back_populates='company_delivery_address'
    )

class Product(Base):
    __tablename__ = 'product'
    pk: Mapped[int] = mapped_column(primary_key=True)
    brand: Mapped[str] = mapped_column(String(50), nullable=False)
    product_number: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )
    product_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )
    unit_of_measure: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )
    supplier_product: Mapped[List['SupplierProduct']] = relationship(
        back_populates='product'
    )

class SupplierProduct(Base):
    __tablename__ = 'supplier_product'
    pk: Mapped[int] = mapped_column(primary_key=True)
    fk_product: Mapped[int] = mapped_column(
        ForeignKey('product.pk'),
        nullable=False
    )
    fk_company: Mapped[int] = mapped_column(
        ForeignKey('company.pk'),
        nullable=False
    )
    company: Mapped['Company'] = relationship(
        back_populates='supplier_product'
    )
    product: Mapped['Product'] = relationship(
        back_populates='supplier_product'
    )
    supplier_product_cost: Mapped[List['SupplierProductCost']] = \
        relationship(back_populates='supplier_product')
    quotation_lineitem: Mapped[List['QuotationLineitem']] = \
        relationship(back_populates='supplier_product')

class SupplierProductCost(Base):
    __tablename__ = 'supplier_product_cost'
    pk: Mapped[int] = mapped_column(primary_key=True)
    fk_supplier_product: Mapped[int] = mapped_column(
        ForeignKey('supplier_product.pk'),
        nullable=False
    )
    currency: Mapped[str] = mapped_column(String(3), nullable=False)
    cost: Mapped[float] = mapped_column(Numeric(7, 3), nullable=False)
    discount: Mapped[float] = mapped_column(
        Numeric(3, 3),
        nullable=False
    )
    calculated_price: Mapped[float] = mapped_column(
        Numeric(7, 3),
        nullable=False
    )
    cost_source: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )
    valid_from: Mapped[datetime] = mapped_column(nullable=False)
    valid_until: Mapped[datetime] = mapped_column(nullable=False)
    is_current: Mapped[bool] = mapped_column(nullable=False)
    supplier_product: Mapped['SupplierProduct'] = relationship(
        back_populates='supplier_product_cost'
    )
    purchase_order_lineitem: Mapped[List['PurchaseOrderLineitem']] = \
        relationship(back_populates='supplier_product_cost')

class Quotation(Base):
    __tablename__ = 'quotation'
    pk: Mapped[int] = mapped_column(primary_key=True)
    fk_company: Mapped[int] = mapped_column(
        ForeignKey('company.pk'),
        nullable=False
    )
    quotation_number: Mapped[str] = mapped_column(
        String(10),
        nullable=False
    )
    date_issued: Mapped[datetime] = mapped_column(nullable=False)
    rfq_number: Mapped[str] = mapped_column(String(50), nullable=True)
    rfq_date: Mapped[date] = mapped_column(nullable=False)
    company: Mapped['Company'] = relationship(
        back_populates='quotation'
    )
    quotation_lineitem: Mapped[List['QuotationLineitem']] = \
        relationship(back_populates='quotation')

class QuotationLineitem(Base):
    __tablename__ = 'quotation_lineitem'
    pk: Mapped[int] = mapped_column(primary_key=True)
    fk_quotation: Mapped[int] = mapped_column(
        ForeignKey('quotation.pk'),
        nullable=False
    )
    fk_supplier_product: Mapped[int] = mapped_column(
        ForeignKey('supplier_product.pk'),
        nullable=False
    )
    customer_description: Mapped[str] = mapped_column(nullable=False)
    additional_notes: Mapped[str] = mapped_column(nullable=True)
    # requested_quantity: Mapped[int] = mapped_column(
        # SmallInteger,
        # nullable=False
    # )
    quoted_quantity: Mapped[int] = mapped_column(
        SmallInteger,
        nullable=False
    )
    unit_price: Mapped[float] = mapped_column(
        Numeric(7, 3),
        nullable=False
        )
    availability: Mapped[str] = mapped_column(nullable=False)
    quotation: Mapped['Quotation'] = relationship(
        back_populates='quotation_lineitem'
    )
    supplier_product: Mapped['SupplierProduct'] = relationship(
        back_populates='quotation_lineitem'
    )
    sales_order_lineitem: Mapped[Optional['SalesOrderLineitem']] = \
        relationship(back_populates='quotation_lineitem')

class SalesOrder(Base):
    __tablename__ = 'sales_order'
    pk: Mapped[int] = mapped_column(primary_key=True)
    fk_company_delivery_address: Mapped[int] = mapped_column(
        ForeignKey('company_delivery_address.pk'),
        nullable=False
    )
    purchase_order_number: Mapped[int] = mapped_column(nullable=False)
    date_issued: Mapped[date] = mapped_column(nullable=False)
    date_received: Mapped[date] = mapped_column(nullable=False)
    purchase_order_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )
    company_delivery_address: Mapped['CompanyDeliveryAddress'] = \
        relationship(back_populates='sales_order')
    sales_order_lineitem: Mapped[List['SalesOrderLineitem']] = \
        relationship(back_populates='sales_order')
    sales_invoice: Mapped[List['SalesInvoice']] = \
        relationship(back_populates='sales_order')

class SalesOrderLineitem(Base):
    __tablename__ = 'sales_order_lineitem'
    pk: Mapped[int] = mapped_column(primary_key=True)
    fk_sales_order: Mapped[int] = mapped_column(
        ForeignKey('sales_order.pk'),
        nullable=False
    )
    fk_quotation_lineitem: Mapped[int] = mapped_column(
        ForeignKey('quotation_lineitem.pk'),
        nullable=True
    )
    customer_description: Mapped[str] = mapped_column(nullable=True)
    notes: Mapped[str] = mapped_column(nullable=True)
    ordered_quantity: Mapped[int] = mapped_column(
        SmallInteger,
        nullable=False
    )
    sales_order: Mapped['SalesOrder'] = relationship(
        back_populates='sales_order_lineitem'
    )
    quotation_lineitem: Mapped[Optional['QuotationLineitem']] = \
        relationship(back_populates='sales_order_lineitem')
    sales_invoice_lineitem: Mapped['SalesInvoiceLineitem'] = \
        relationship(back_populates='sales_order_lineitem')
    purchase_order_lineitem: Mapped[List['PurchaseOrderLineitem']] = \
        relationship(back_populates='sales_order_lineitem')

class SalesInvoice(Base):
    __tablename__ = 'sales_invoice'
    pk: Mapped[int] = mapped_column(primary_key=True)
    fk_sales_order: Mapped[int] = mapped_column(
        ForeignKey('sales_order.pk'),
        nullable=False
    )
    sales_invoice_number: Mapped[int] = mapped_column(nullable=False)
    delivery_receipt_number: Mapped[int] = mapped_column(nullable=False)
    sales_order: Mapped['SalesOrder'] = relationship(
        back_populates='sales_invoice'
    )
    sales_invoice_lineitem: Mapped[List['SalesInvoiceLineitem']] = \
        relationship(back_populates='sales_invoice')

class SalesInvoiceLineitem(Base):
    __tablename__ = 'sales_invoice_lineitem'
    pk: Mapped[int] = mapped_column(primary_key=True)
    fk_sales_invoice: Mapped[int] = mapped_column(
        ForeignKey('sales_invoice.pk'),
        nullable=False
    )
    fk_sales_order_lineitem: Mapped[int] = mapped_column(
        ForeignKey('sales_order_lineitem.pk'),
        nullable=False
    )
    invoiced_quantity: Mapped[int] = mapped_column(
        SmallInteger,
        nullable=False
    )
    sales_invoice: Mapped['SalesInvoice'] = relationship(
        back_populates='sales_invoice_lineitem'
    )
    sales_order_lineitem: Mapped['SalesOrderLineitem'] = relationship(
        back_populates='sales_invoice_lineitem'
    )

class PurchaseOrder(Base):
    __tablename__ = 'purchase_order'
    pk: Mapped[int] = mapped_column(primary_key=True)
    fk_company: Mapped[int] = mapped_column(
        ForeignKey('company.pk'),
        nullable=False
    )
    purchase_order_number: Mapped[int] = mapped_column(
        nullable=False
    )
    date_issued: Mapped[datetime] = mapped_column(nullable=False)
    company: Mapped['Company'] = relationship(
        back_populates='purchase_order'
    )
    purchase_order_lineitem: Mapped[List['PurchaseOrderLineitem']] = \
        relationship(back_populates='purchase_order')

class PurchaseOrderLineitem(Base):
    __tablename__ = 'purchase_order_lineitem'
    pk: Mapped[int] = mapped_column(primary_key=True)
    fk_purchase_order: Mapped[int] = mapped_column(
        ForeignKey('purchase_order.pk'),
        nullable=False
    )
    fk_sales_order_lineitem: Mapped[int] = mapped_column(
        ForeignKey('sales_order_lineitem.pk'),
        nullable=False
    )
    fk_supplier_product_cost: Mapped[int] = mapped_column(
        ForeignKey('supplier_product_cost.pk'),
        nullable=False
    )
    ordered_quantity: Mapped[int] = mapped_column(
        SmallInteger,
        nullable=False
    )
    purchase_order: Mapped['PurchaseOrder'] = relationship(
        back_populates='purchase_order_lineitem'
    )
    sales_order_lineitem: Mapped['SalesOrderLineitem'] = relationship(
        back_populates='purchase_order_lineitem'
    )
    supplier_product_cost: Mapped['SupplierProductCost'] = relationship(
        back_populates='purchase_order_lineitem'
    )

