
from app.shared.view_mixins import TimestampedViewMixin

class TransactionPresenter:

    VISIBLE_COLUMNS = [
        "barcode", "product_name", "price_at_scan", "quantity", "created_at", "price_per_100g"
    ]
    COLUMN_LABELS = {
		"id": "ID",
        "product_name": "Product Name",
		"product_id": "Product ID",
		"price_at_scan": "Price",
		"quantity": "Qty",
		"created_at": "Date",
        "price_per_100g": "Per 100g",
        "barcode": "Barcode"
	}
    
    @classmethod
    def build_columns(cls) -> list[dict]:
        return [{"key": c, "label": cls.COLUMN_LABELS.get(c, c)} for c in cls.VISIBLE_COLUMNS]

class TransactionViewModel(TimestampedViewMixin):
    def __init__(self, txn, tz):
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
    def price_label(self):
        return f"${self.price_at_scan:.2f}"
    
    @property
    def price_per_100g_label(self):
        return f"${self.price_per_100g:.2f}"
    
    @property
    def created_at_label(self):
        return self.format(self.created_at, self._tz, "%d.%m.%Y")



class ProductPresenter:

    VISIBLE_COLUMNS = [
        "barcode", "name", "category", "net_weight_display", "calories_per_100g"
    ]
    COLUMN_LABELS = {
		"id": "ID",
		"name": "Product Name",
		"category": "Category",
		"barcode": "Barcode",
		"net_weight_display": "Net Weight",
		"unit_type": "Unit",
		"calories_per_100g": "Cals per 100g",
		"created_at": "Created",
	}

    @classmethod
    def build_columns(cls) -> list[dict]:
        return [{"key": c, "label": cls.COLUMN_LABELS.get(c, c)} for c in cls.VISIBLE_COLUMNS]
    
class ProductViewModel(TimestampedViewMixin):
    def __init__(self, product, tz):
        self.id = product.id
        self.barcode = product.barcode
        self.name = product.name
        self.category = product.category
        self.net_weight = product.net_weight
        self.unit_type = product.unit_type
        self.calories_per_100g = product.calories_per_100g
        self._tz = tz

    @property
    def net_weight_display(self):
        return f"{self.net_weight:.2f} ({self.unit_type.value})"
    
    @property
    def calories_display(self):
        return int(self.calories_per_100g) if self.calories_per_100g else "--"