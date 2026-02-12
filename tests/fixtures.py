from decimal import Decimal

from app.modules.groceries.models import (
    Product,
    ProductCategoryEnum,
    ShoppingList,
    ShoppingListItem,
    Transaction,
    UnitEnum,
)


def product_fixture(**overrides) -> Product:
    return Product(
        id=overrides.get("id", 1),
        name=overrides.get("name", "Test Apple"),
        category=overrides.get("category", ProductCategoryEnum.FRUITS),
        barcode=overrides.get("barcode", "1234567890123"),
        net_weight=overrides.get("net_weight", Decimal("150.0")),
        unit_type=overrides.get("unit_type", UnitEnum.G),
        calories_per_100g=overrides.get("calories_per_100g", Decimal(52)),
        deleted_at=overrides.get("deleted_at"),
    )


def transaction_fixture(product: Product = None, **overrides) -> Transaction:
    product = product or product_fixture()
    return Transaction(
        id=overrides.get("id", 1),
        product_id=overrides.get("product_id", product.id),
        product=product,
        price_at_scan=overrides.get("price_at_scan", Decimal("3.49")),
        quantity=overrides.get("quantity", 2),
    )


def shopping_list_fixture(**overrides) -> ShoppingList:
    return ShoppingList(
        id=overrides.get("id", 1),
        name=overrides.get("name", "Weekly List"),
    )


def shopping_list_item_fixture(
    product: Product | None = None, shopping_list: ShoppingList | None = None, **overrides
) -> ShoppingListItem:
    product = product or product_fixture()
    shopping_list = shopping_list or shopping_list_fixture()
    return ShoppingListItem(
        id=overrides.get("id", 1),
        product_id=overrides.get("product_id", product.id),
        product=product,
        shopping_list_id=overrides.get("shopping_list_id", shopping_list.id),
        shopping_list=shopping_list,
        quantity_wanted=overrides.get("quantity_wanted", 3),
    )
