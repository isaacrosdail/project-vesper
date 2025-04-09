# Handles DB setup/functionality & grocery related DB functions
from core.database import get_session, engine
from sqlalchemy.orm import declarative_base, relationship, joinedload
from sqlalchemy import ForeignKey

from sqlalchemy import Table, Column, Integer, String, DECIMAL, Float, Date

Base = declarative_base()

# Product Model for database of products known
class Product(Base):
	__tablename__ = "product"

	product_id = Column(Integer, primary_key=True)
	product_name = Column(String(100), nullable=False)
	barcode = Column(String(64), unique=True, nullable=False)
	price = Column(DECIMAL(10,2), nullable=False)
	net_weight = Column(Float, nullable=False)

	# Human-readable column names
	COLUMN_LABELS = {
		"product_id": "Product ID",
		"product_name": "Product Name",
		"barcode": "Barcode",
		"price": "Price",
		"net_weight": "Net Weight (g)",
	}

# Transaction Model for 'inventory'
class Transaction(Base):
	__tablename__ = "transaction"

	transaction_id = Column(Integer, primary_key=True)
	product_id = Column(Integer, ForeignKey("product.product_id"), nullable=False)
	price_at_scan = Column(DECIMAL(10,2), nullable=False)
	quantity = Column(Integer, nullable=False)
	date_scanned = Column(Date)

	product = relationship("Product")

	# Human-readable column names
	COLUMN_LABELS = {
		"transaction_id": "Transaction #",
		"price_at_scan": "Price",
		"quantity": "Quantity",
	}

Base.metadata.create_all(engine)