
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.modules.groceries.models import Product, Transaction


from app.modules.groceries.models import ProductCategoryEnum as Category
from app.modules.groceries.models import UnitEnum as UnitType
from app.shared.view_mixins import TimestampedViewMixin, BasePresenter

class TransactionPresenter(BasePresenter):

    VISIBLE_COLUMNS = [
        "product_name", "price_at_scan", "price_per_100g", "created_at"
    ]

    COLUMN_CONFIG = {
    "product_name": {"label": "Product Name", "priority": "essential"},
    "price_at_scan": {"label": "Price (qty)", "priority": "essential"},
    "quantity": {"label": "Qty", "priority": "desktop-only"},
    "created_at": {"label": "Date", "priority": "essential"},
    "price_per_100g": {"label": "Price (100g)", "priority": "desktop-only"}
    }

class TransactionViewModel(TimestampedViewMixin):
    def __init__(self, txn: 'Transaction', tz: str):
        self.id = txn.id
        self.product_id = txn.product_id
        self.product_name = txn.product.name
        self.barcode = txn.product.barcode
        self.price_at_scan = txn.price_at_scan
        self.quantity = txn.quantity
        self.created_at = txn.created_at
        self.price_per_100g = txn.price_per_100g        # calculated field
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

    VISIBLE_COLUMNS = [
        "barcode", "name", "category", "net_weight_display", "calories_per_100g"
    ]
    COLUMN_CONFIG = {
        "id": {"label": "ID", "priority": "desktop-only"},
        "name": {"label": "Product Name", "priority": "essential"},
        "category": {"label": "Category", "priority": "essential"},
        "barcode": {"label": "Barcode", "priority": "desktop-only"},
        "net_weight_display": {"label": "Net Weight", "priority": "desktop-only", "sort_field": "net_weight"},
        "unit_type": {"label": "Unit", "priority": "desktop-only"},
        "calories_per_100g": {"label": "Calories (per 100g)", "priority": "essential"},
        "created_at": {"label": "Created", "priority": "desktop-only"}
    }

    
class ProductViewModel(TimestampedViewMixin):
    CATEGORY_LABELS = {
        Category.FRUITS: "Fruits",
        Category.VEGETABLES: "Vegetables",
        Category.LEGUMES: "Legumes",
        Category.GRAINS: "Grains",
        Category.BAKERY: "Bakery",
        Category.DAIRY_EGGS: "Dairy & Eggs",
        Category.MEATS: "Meats",
        Category.SEAFOOD: "Seafood",
        Category.FATS_OILS: "Fats/Oils",
        Category.SNACKS: "Snacks",
        Category.SWEETS: "Sweets",
        Category.BEVERAGES: "Beverages",
        Category.CONDIMENTS_SAUCES: "Condiments & Sauces",
        Category.PROCESSED_CONVENIENCE: "Processed & Convenience",
        Category.SUPPLEMENTS: "Supplements",
    }
    UNIT_TYPE_LABELS = {
        UnitType.G: "g",
        UnitType.KG: "kg",
        UnitType.OZ: "oz",
        UnitType.LB: "lb",
        UnitType.ML: "ml",
        UnitType.L: "l",
        UnitType.FL_OZ: "fl oz",
        UnitType.EA: "ea.",
    }

    def __init__(self, product: 'Product', tz: str):
        self.id = product.id
        self.barcode = product.barcode
        self.name = product.name
        self.category = product.category
        self.net_weight = product.net_weight
        self.unit_type = product.unit_type
        self.calories_per_100g = product.calories_per_100g
        self._tz = tz

    @property
    def barcode_label(self) -> str:
        return str(self.barcode) if self.barcode is not None else "--"

    @property
    def category_label(self) -> str:
        return ProductViewModel.CATEGORY_LABELS[self.category]

    @property
    def net_weight_label(self) -> str:
        return f"{self.net_weight:.2f} ({ProductViewModel.UNIT_TYPE_LABELS[self.unit_type]})"
    
    @property
    def calories_label(self) -> str:
        if self.calories_per_100g:
            return "--"
        return str(int(round(self.calories_per_100g)))