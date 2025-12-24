"""Database models for Invoice Processor"""

from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, Enum, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
import enum

Base = declarative_base()


class PaymentStatus(enum.Enum):
    """Payment status enum"""
    PENDING = "pending"
    PARTIAL = "partial"
    PAID = "paid"
    OVERDUE = "overdue"


class InvoiceType(enum.Enum):
    """Invoice type enum"""
    PURCHASE = "purchase"  # Buying from supplier
    SALES = "sales"        # Selling to customer


# ========== MASTER DATA ==========

class Supplier(Base):
    """Suppliers - Companies we buy from"""
    __tablename__ = 'suppliers'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    contact_person = Column(String(100))
    phone = Column(String(20))
    email = Column(String(100))
    address = Column(Text)
    gstin = Column(String(15))  # GST Number
    payment_terms_days = Column(Integer, default=30)  # Net 30
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    purchase_invoices = relationship("PurchaseInvoice", back_populates="supplier")


class Customer(Base):
    """Customers - Retailers/businesses we sell to"""
    __tablename__ = 'customers'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    contact_person = Column(String(100))
    phone = Column(String(20))
    email = Column(String(100))
    address = Column(Text)
    gstin = Column(String(15))
    credit_limit = Column(Float, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    sales_invoices = relationship("SalesInvoice", back_populates="customer")


class Item(Base):
    """Items - Products in catalog"""
    __tablename__ = 'items'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    hsn_code = Column(String(10))  # HSN/SAC code for GST
    unit = Column(String(20), default="piece")  # piece, box, kg, etc.
    category = Column(String(100))  # Bolts, Screws, Tools, etc.
    current_stock = Column(Float, default=0)
    min_stock_level = Column(Float, default=0)  # For alerts
    last_cost_price = Column(Float, default=0)  # Latest purchase price
    default_selling_price = Column(Float, default=0)
    default_margin_percent = Column(Float, default=20)  # Default 20% margin
    gst_rate = Column(Float, default=18)  # GST percentage
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    purchase_items = relationship("PurchaseItem", back_populates="item")
    sales_items = relationship("SalesItem", back_populates="item")


# ========== PURCHASE INVOICES ==========

class PurchaseInvoice(Base):
    """Purchase Invoices - We buy from suppliers"""
    __tablename__ = 'purchase_invoices'
    
    id = Column(Integer, primary_key=True)
    supplier_id = Column(Integer, ForeignKey('suppliers.id'), nullable=False)
    
    # Invoice details
    invoice_number = Column(String(50), unique=True, nullable=False)
    invoice_date = Column(DateTime, nullable=False)
    due_date = Column(DateTime)
    
    # Amounts
    subtotal = Column(Float, default=0)  # Before GST
    gst_amount = Column(Float, default=0)
    total_amount = Column(Float, default=0)  # After GST
    
    # Payment
    payment_status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING)
    amount_paid = Column(Float, default=0)
    
    # Metadata
    original_file_path = Column(String(500))  # Path to uploaded invoice
    extracted_text = Column(Text)  # Full OCR text
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    processed_by = Column(String(50), default="AI")  # AI or username
    
    # Relationships
    supplier = relationship("Supplier", back_populates="purchase_invoices")
    items = relationship("PurchaseItem", back_populates="invoice", cascade="all, delete-orphan")


class PurchaseItem(Base):
    """Line items in purchase invoice"""
    __tablename__ = 'purchase_items'
    
    id = Column(Integer, primary_key=True)
    invoice_id = Column(Integer, ForeignKey('purchase_invoices.id'), nullable=False)
    item_id = Column(Integer, ForeignKey('items.id'))
    
    # Item details (as on invoice)
    item_name = Column(String(200), nullable=False)  # Raw name from invoice
    quantity = Column(Float, nullable=False)
    unit = Column(String(20), default="piece")
    unit_price = Column(Float, nullable=False)
    
    # Calculated
    subtotal = Column(Float, nullable=False)  # qty * unit_price
    gst_rate = Column(Float, default=18)
    gst_amount = Column(Float, default=0)
    total = Column(Float, nullable=False)  # subtotal + GST
    
    # Relationships
    invoice = relationship("PurchaseInvoice", back_populates="items")
    item = relationship("Item", back_populates="purchase_items")


# ========== SALES INVOICES ==========

class SalesInvoice(Base):
    """Sales Invoices - We sell to customers"""
    __tablename__ = 'sales_invoices'
    
    id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey('customers.id'), nullable=False)
    
    # Invoice details
    invoice_number = Column(String(50), unique=True, nullable=False)
    invoice_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    due_date = Column(DateTime)
    
    # Amounts
    subtotal = Column(Float, default=0)
    gst_amount = Column(Float, default=0)
    total_amount = Column(Float, default=0)
    
    # Profit tracking
    total_cost = Column(Float, default=0)  # What we paid for these items
    total_profit = Column(Float, default=0)  # Selling price - cost
    
    # Payment
    payment_status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING)
    amount_paid = Column(Float, default=0)
    
    # Metadata
    generated_pdf_path = Column(String(500))
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(String(50), default="System")
    
    # Relationships
    customer = relationship("Customer", back_populates="sales_invoices")
    items = relationship("SalesItem", back_populates="invoice", cascade="all, delete-orphan")


class SalesItem(Base):
    """Line items in sales invoice"""
    __tablename__ = 'sales_items'
    
    id = Column(Integer, primary_key=True)
    invoice_id = Column(Integer, ForeignKey('sales_invoices.id'), nullable=False)
    item_id = Column(Integer, ForeignKey('items.id'), nullable=False)
    
    # Sale details
    quantity = Column(Float, nullable=False)
    unit_price = Column(Float, nullable=False)  # Selling price
    
    # Cost & profit
    cost_price = Column(Float, nullable=False)  # What we paid
    profit_per_unit = Column(Float, default=0)
    total_profit = Column(Float, default=0)
    
    # Calculated
    subtotal = Column(Float, nullable=False)
    gst_rate = Column(Float, default=18)
    gst_amount = Column(Float, default=0)
    total = Column(Float, nullable=False)
    
    # Relationships
    invoice = relationship("SalesInvoice", back_populates="items")
    item = relationship("Item", back_populates="sales_items")


# ========== DATABASE SETUP ==========

def get_engine(database_url="sqlite:///invoice_data.db"):
    """Create database engine"""
    return create_engine(database_url, echo=False)


def init_database(engine=None):
    """Initialize database - create all tables"""
    if engine is None:
        engine = get_engine()
    
    Base.metadata.create_all(engine)
    print("✅ Database initialized!")
    return engine


def get_session(engine=None):
    """Get database session"""
    if engine is None:
        engine = get_engine()
    
    Session = sessionmaker(bind=engine)
    return Session()


# Initialize on import
if __name__ == "__main__":
    # Test database creation
    engine = init_database()
    print("Database setup complete!")
