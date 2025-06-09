# Handles DB models for grocery module
from datetime import datetime, timezone

from sqlalchemy import (Column, DateTime, Float, ForeignKey, Integer, Numeric,
                        String)
from sqlalchemy.orm import relationship

from app.core.db_base import Base


# Product Model for database of products known
class Product(Base):

	product_name = Column(String(100), nullable=False)
	barcode = Column(String(64), unique=True, nullable=False)
	price = Column(Numeric(10,2), nullable=True) # To be removed
	net_weight = Column(Float, nullable=False)

	# Human-readable column names
	COLUMN_LABELS = {
		"id": "Product ID",
		"product_name": "Product Name",
		"barcode": "Barcode",
		"price": "Price", # To be removed
		"net_weight": "Net Weight (g)",
	}

# Transaction Model for 'inventory'
class Transaction(Base):

	product_id = Column(Integer, ForeignKey("product.id"), nullable=False)
	price_at_scan = Column(Numeric(10,2), nullable=False)
	quantity = Column(Integer, nullable=False)

	product = relationship("Product")

	# Human-readable column names
	COLUMN_LABELS = {
		"id": "Transaction #",
		"price_at_scan": "Price",
		"quantity": "Quantity",
	}