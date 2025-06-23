from decimal import Decimal

def calculate_price_per_100g(price: Decimal, weight: float) -> Decimal:
    """
    Calculate price per 100g for grocery items.
    Args:
        price: Total price of the item in currency units
        weight: Net weight of the item in grams.
    Returns:
        Price per 100g as a float
    Raises:
        Nothing yet
    """
    weight_decimal = Decimal(str(weight))
    # str handles floating point weirdness because...yeah idk
    return (price / weight_decimal) * 100

def get_price_per_100g(grocery_item: object) -> Decimal:
    """Convenience wrapper for grocery database objects"""
    return calculate_price_per_100g(grocery_item.price_at_scan, grocery_item.product.net_weight)