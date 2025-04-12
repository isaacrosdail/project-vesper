# Handles DB models for grocery module

from sqlalchemy.orm import relationship, joinedload
from sqlalchemy import ForeignKey
#from app.database import Base
from app.db_base import Base

from sqlalchemy import Table, Column, Integer, String, DECIMAL, Float, Date, Numeric

# Product Model for database of products known
class Product(Base):
	__tablename__ = "product"

	product_id = Column(Integer, primary_key=True)
	product_name = Column(String(100), nullable=False)
	barcode = Column(String(64), unique=True, nullable=False)
	price = Column(Numeric(10,2), nullable=False)
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
	price_at_scan = Column(Numeric(10,2), nullable=False)
	quantity = Column(Integer, nullable=False)
	date_scanned = Column(Date)

	product = relationship("Product")

	# Human-readable column names
	COLUMN_LABELS = {
		"transaction_id": "Transaction #",
		"price_at_scan": "Price",
		"quantity": "Quantity",
	}