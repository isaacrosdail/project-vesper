# Handles DB models for grocery module
from datetime import datetime, timezone

from sqlalchemy import (Column, DateTime, Float, ForeignKey, Integer, Numeric,
                        String)
from sqlalchemy.orm import relationship

from app.core.db_base import Base


# Product Model for database of products known
class Product(Base):
	__tablename__ = "product"

	product_id = Column(Integer, primary_key=True)
	product_name = Column(String(100), nullable=False)
	barcode = Column(String(64), unique=True, nullable=False)
	price = Column(Numeric(10,2), nullable=True) # To be removed
	net_weight = Column(Float, nullable=False)

	# Human-readable column names
	COLUMN_LABELS = {
		"product_id": "Product ID",
		"product_name": "Product Name",
		"barcode": "Barcode",
		"price": "Price", # To be removed
		"net_weight": "Net Weight (g)",
	}

# Transaction Model for 'inventory'
class Transaction(Base):
	__tablename__ = "transaction"

	transaction_id = Column(Integer, primary_key=True)
	product_id = Column(Integer, ForeignKey("product.product_id"), nullable=False)
	price_at_scan = Column(Numeric(10,2), nullable=False)
	quantity = Column(Integer, nullable=False)
	date_scanned = (Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)))

	product = relationship("Product")

	# Human-readable column names
	COLUMN_LABELS = {
		"transaction_id": "Transaction #",
		"price_at_scan": "Price",
		"quantity": "Quantity",
	}