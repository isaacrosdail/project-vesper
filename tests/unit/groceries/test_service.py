
"""Unit tests for groceries service; pure logic, no database."""
from decimal import Decimal

from app.modules.groceries.models import (
    MealEnum,
    NutritionLog,
    Product,
    ProductCategoryEnum,
    RecipeIngredient,
    UnitEnum,
)
from app.modules.groceries.service import compute_shortfalls, summarize_macros


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

def ingredient(product, amount, unit=UnitEnum.G) -> RecipeIngredient:
    return RecipeIngredient(
        product_id=product.id,
        product=product,
        amount_value=amount,
        amount_units=unit,
    )


def test_product_absent_from_inventory_is_full_deficit():
    eggs = product_fixture(id=1, name="Eggs", net_weight=Decimal(10))
    [sf] = compute_shortfalls([ingredient(eggs, 30)], qty_map={})
    assert sf.deficit_value == 30
    assert sf.packages_needed == 3
    assert sf.product_name == "Eggs"


def test_partial_stock_deficit_is_needed_minus_on_hand():
    rice = product_fixture(id=1, net_weight=Decimal(100))
    [sf] = compute_shortfalls([ingredient(rice, 250)], qty_map={1: Decimal(100)})
    assert sf.deficit_value == 150   # not the raw 250
    assert sf.packages_needed == 2   # ceil(150/100)


def test_exact_stock_is_ready():
    rice = product_fixture(id=1, net_weight=Decimal(100))
    assert compute_shortfalls([ingredient(rice, 200)], qty_map={1: Decimal(200)}) == []


def test_deficit_exactly_one_package_does_not_round_to_two():
    milk = product_fixture(id=1, net_weight=Decimal(100))
    [sf] = compute_shortfalls([ingredient(milk, 300)], qty_map={1: Decimal(200)})
    assert sf.packages_needed == 1


def test_fractional_net_weight_on_missing_branch():
    # regression: Decimal net_weight * float used to raise TypeError here
    butter = product_fixture(id=1, net_weight=Decimal("10.5"))
    [sf] = compute_shortfalls([ingredient(butter, 21)], qty_map={1: Decimal("10.5")})
    assert sf.deficit_value == 10.5
    assert sf.packages_needed == 1


def test_only_missing_ingredients_reported():
    rice = product_fixture(id=1, net_weight=Decimal(100))
    eggs = product_fixture(id=2, name="Eggs", net_weight=Decimal(10))
    result = compute_shortfalls(
        [ingredient(rice, 100), ingredient(eggs, 30)],
        qty_map={1: Decimal(500)},  # rice stocked, eggs absent
    )
    assert [sf.product_id for sf in result] == [2]


def test_no_ingredients_is_ready():
    assert compute_shortfalls([], qty_map={}) == []


## summarize_macros()
def test_macros_summary_core():
    logs = []
    targets_dict = {"calories": 2200, "protein": 149, "carbs": 248, "fat": 68, "sodium": 0, "potassium": 0}
    fields = ["calories", "protein", "carbs", "fat", "sodium", "potassium"]
    result, meals = summarize_macros(logs, targets_dict, logged_days=1)

    assert result["calories"] == {"actual": 0, "target": 2200, "pct": 0}
    assert meals == {}

def test_single_log_sums_and_pcts():
    logs = [NutritionLog(calories=1100, protein=74, carbs=124, fat=34, sodium=800, potassium=1000, meal="lunch")]
    targets_dict = {"calories": 2200, "protein": 149, "carbs": 248, "fat": 68, "sodium": 0, "potassium": 0}
    fields = ["calories", "protein", "carbs", "fat", "sodium", "potassium"]
    result, meals = summarize_macros(logs, targets_dict, logged_days=1)
    assert result["calories"] == {"actual": 1100, "target": 2200, "pct": 50}
    assert meals == {"lunch": 1100}

def test_averages_over_logged_days():
    logs = [
        NutritionLog(calories=1000, protein=100, carbs=100, fat=30, sodium=900, potassium=1200, meal="lunch"),   # day 1
        NutritionLog(calories=1000, protein=100, carbs=100, fat=30, sodium=900, potassium=1200, meal="lunch"),   # day 1
        NutritionLog(calories=1000, protein=50, carbs=100, fat=30, sodium=900, potassium=1200, meal="dinner"),   # day 2
    ]
    targets_dict = {"calories": 2200, "protein": 149, "carbs": 248, "fat": 68, "sodium": 0, "potassium": 0}
    fields = ["calories", "protein", "carbs", "fat", "sodium", "potassium"]
    result, meals = summarize_macros(logs, targets_dict, logged_days=2)
    assert result["calories"]["actual"] == 1500
    assert result["calories"]["pct"] == 68   # 1500/2200
    assert meals[MealEnum.LUNCH] == 2000
##
