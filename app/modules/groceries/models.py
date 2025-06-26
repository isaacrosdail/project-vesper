# Handles DB models for grocery module
from datetime import datetime, timezone

from sqlalchemy import (Column, DateTime, Float, ForeignKey, Integer, Numeric,
                        String)
from sqlalchemy.orm import relationship

from app.core.db_base import Base


# Product Model for database of products known
class Product(Base):

	product_name = Column(String(100), nullable=False)
	category = Column(String(100), nullable=True) # "dairy", "produce", etc
	barcode = Column(String(64), unique=True, nullable=False)
	net_weight = Column(Float, nullable=False)
	unit_type = Column(String(20), nullable=False) # grams, oz, ml, etc
	calories_per_100g = Column(Float, nullable=True)
	deleted_at = Column(DateTime, nullable=True, default=None)

	def __str__(self):
		return f"{self.product_name} ({self.barcode})"

	# Human-readable column names
	COLUMN_LABELS = {
		"id": "ID",
		"product_name": "Product Name",
		"category": "Category",
		"barcode": "Barcode",
		"net_weight": "Net Weight",
		"unit_type": "Unit Type",
		"calories_per_100g": "Kcals per 100g"
	}

# Transaction Model for 'inventory'
class Transaction(Base):

	product_id = Column(Integer, ForeignKey("product.id"), nullable=False)
	price_at_scan = Column(Numeric(10,2), nullable=False)
	quantity = Column(Integer, nullable=False)

	product = relationship("Product")

	def __str__(self):
		return f"Transaction:{self.id}: {self.quantity}x {self.product.product_name} @ {self.price_at_scan}"

	# Human-readable column names
	COLUMN_LABELS = {
		"id": "ID",
		"price_at_scan": "Price",
		"quantity": "Quantity",
	}