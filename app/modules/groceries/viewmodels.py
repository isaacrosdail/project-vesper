from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

if TYPE_CHECKING:
    from app.modules.groceries.models import Product, Transaction


from app.shared.view_mixins import BasePresenter, BaseViewModel


class TransactionPresenter(BasePresenter):
    VISIBLE_COLUMNS: ClassVar[list[str]] = [
        "product_name",
        "price_at_scan",
        "price_per_100g",
        "created_at",
    ]

    COLUMN_CONFIG: ClassVar[dict[str, dict[str, str]]] = {
        "product_name": {"label": "Product Name", "priority": "essential"},
        "price_at_scan": {"label": "Price (qty)", "priority": "essential"},
        "quantity": {"label": "Qty", "priority": "desktop-only"},
        "created_at": {"label": "Date", "priority": "essential"},
        "price_per_100g": {"label": "Price (100g)", "priority": "desktop-only"},
    }


class TransactionViewModel(BaseViewModel):
    __slots__ = (
        "_tz",
        "barcode",
        "id",
        "price_at_scan",
        "price_per_100g",
        "product_id",
        "product_name",
        "quantity",
        "subtype",
    )

    def __init__(self, txn: Transaction, tz: str) -> None:
        self.created_at_local = txn.created_at_local
        self.product_id = txn.product_id
        self.product_name = txn.product.name
        self.barcode = txn.product.barcode
        self.price_at_scan = txn.price_at_scan
        self.quantity = txn.quantity
        self.price_per_100g = txn.price_per_100g
        self.subtype = txn.subtype
        self.id = txn.id
        self._tz = tz

    @property
    def price_label(self) -> str:
        total_price = self.price_at_scan * self.quantity
        return f"${total_price:.2f} ({self.quantity}x)"

    @property
    def price_per_100g_label(self) -> str:
        return f"${self.price_per_100g:.2f}"

    @property
    def created_at_label(self) -> str:
        return self.format_created_at_label()


class ProductPresenter(BasePresenter):
    VISIBLE_COLUMNS: ClassVar[list[str]] = [
        "barcode",
        "name",
        "category",
        "net_weight_display",
        "calories_per_100g",
    ]
    COLUMN_CONFIG: ClassVar[dict[str, dict[str, str]]] = {
        "id": {"label": "ID", "priority": "desktop-only"},
        "name": {"label": "Product Name", "priority": "essential"},
        "category": {"label": "Category", "priority": "essential"},
        "barcode": {"label": "Barcode", "priority": "desktop-only"},
        "net_weight_display": {
            "label": "Net Weight",
            "priority": "desktop-only",
            "sort_field": "net_weight",
        },
        "unit_type": {"label": "Unit", "priority": "desktop-only"},
        "calories_per_100g": {"label": "Calories (per 100g)", "priority": "essential"},
        "created_at": {"label": "Created", "priority": "desktop-only"},
    }


class ProductViewModel(BaseViewModel):
    __slots__ = (
        "_tz",
        "barcode",
        "calories_per_100g",
        "category",
        "id",
        "name",
        "net_weight",
        "subtype",
        "unit_type"
    )

    def __init__(self, product: Product, tz: str) -> None:
        self.id = product.id
        self.barcode = product.barcode
        self.name = product.name
        self.category = product.category
        self.net_weight = product.net_weight
        self.unit_type = product.unit_type
        self.calories_per_100g = product.calories_per_100g
        self.subtype = product.subtype
        self._tz = tz

    @property
    def barcode_label(self) -> str:
        return str(self.barcode) if self.barcode is not None else "--"

    @property
    def category_label(self) -> str:
        return self.category.label

    @property
    def net_weight_label(self) -> str:
        return f"{self.net_weight:.2f} ({self.unit_type.label})"

    @property
    def calories_label(self) -> str:
        if not self.calories_per_100g:
            return "--"
        return str(round(self.calories_per_100g))
