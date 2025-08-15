from decimal import Decimal

from app.modules.groceries.pricing import calculate_price_per_100g


def test_calc_price_per_100g():
    # $2.50 for 100g should be 2.50 per 100g lmao
    result = calculate_price_per_100g(Decimal('2.50'), 100)
    assert result == Decimal('2.50')