from datetime import datetime
from decimal import Decimal
from zoneinfo import ZoneInfo

import pytest

from app._infra.database import db_session
from app.modules.groceries.models import (
    InventoryLedgerEventTypeEnum,
    MealEnum,
    Product,
    ProductCategoryEnum,
    UnitEnum,
)
from app.modules.groceries.schemas import (
    RecipeCreate,
    RecipeIngredientCreate,
    TransactionPatch,
)
from app.modules.groceries.service import create_groceries_service
from app.shared.exceptions import ServiceError


@pytest.fixture
def groceries_service(logged_in_user):
    return create_groceries_service(db_session, user_id=logged_in_user.id, user_tz="UTC")

def test_purchase_appends_ledger_and_updates_inventory(groceries_service, sample_products):
    product = sample_products[0]
    groceries_service.create_transaction({
        "product_id": product.id, "price_at_scan": "2.50", "quantity": 2,
    })

    entries = groceries_service.inventory_ledger_repo.get_all_for_product(product.id)
    assert len(entries) == 1
    assert entries[0].event_type == InventoryLedgerEventTypeEnum.PURCHASE
    assert entries[0].qty_delta == 2 * product.net_weight  # base units, not package count

    inv = groceries_service.product_inventory_repo.get_by_product_id(product.id)
    assert inv.qty_on_hand == entries[0].qty_delta


## Using just the calculation for qty_delta = quantity_change * product.net_weight * product.unit_type.factor
# would result in drift when correcting when product net_weight changes:
# EX: Mar1 net_weight = 500 txn for 2 items, qty_delta +1000 -> ledger gets +1000
#     June we change net_weight to 450    -> ledger still at 1000
#     Jul1 we delete the Mar1 transaction:
#                 count * net_weight * factor
# Correction calc:  2   *     450    * 1
# Result: ledger -900 -> now stands at 100g, NOT 0g. We have a phantom 100g.
## FIX: Corrections need to negate what was recorded, never re-derive it - this requires a link from src to entries.
def test_delete_after_net_weight_change_reverses_exactly(groceries_service, logged_in_user):
    product = Product(user_id=logged_in_user.id, name="Apples", category=ProductCategoryEnum.FRUITS, net_weight=Decimal(500), unit_type=UnitEnum.G)
    db_session.add(product)
    db_session.flush() # ensure we have product.id?
    # 1. Should result in ledger of +1500g
    txn = groceries_service.create_transaction({
        "product_id": product.id, "price_at_scan": "2.50", "quantity": 3,
    })
    # 2. Alter net_weight of product
    product.net_weight = Decimal(300)

    # 3. Second transaction: same product, same price, same day
    # Should hit the increment quantity branch
    # Ledger: +2 @ net_weight = 300 -> +600g for a ledger total of 2100g
    # txn.quantity now 5
    # Bugged would re-derive under new net_weight and leave 600g phantom
    groceries_service.create_transaction({
        "product_id": product.id, "price_at_scan": "2.50", "quantity": 2,
    })
    # Ensure 2 ledger rows now exist and carry the same transaction_id
    entries = groceries_service.inventory_ledger_repo.get_all_for_product(product.id)
    assert len(entries) == 2
    assert entries[0].transaction_id == entries[1].transaction_id

    # 4. Remove the transaction
    groceries_service.delete_transaction(txn.id)

    # 4. Assert that the SUM(qty_delta) for this product from ledger is 0g, NOT 600g?
    ledger_sum = groceries_service.inventory_ledger_repo.get_sum_deltas_for_product(product.id)
    assert ledger_sum == 0

def test_update_transaction_blah(groceries_service, logged_in_user):
    product = Product(
        user_id=logged_in_user.id, name="Apples", category=ProductCategoryEnum.FRUITS, net_weight=Decimal(500), unit_type=UnitEnum.G
    )
    db_session.add(product)
    db_session.flush()
    # txn1: 3 @ 500g -> ledger +1500
    # then net_weight changes to 300
    # txn1 update: quantity 3 -> 5, same price
    txn1 = groceries_service.create_transaction({
        "product_id": product.id, "price_at_scan": "2.50", "quantity": 3,
    })
    db_session.flush()

    product.net_weight = Decimal(300)

    # update 3 -> 5
    txn = TransactionPatch(quantity=5)
    groceries_service.update_transaction(txn, txn1.id)

    # correction row for latter 2 qty should use same net_weight as first 3:
    # original 1500 ledger + (new 2 @ same 500g each = 1000) = 2500
    ledger_sum = groceries_service.inventory_ledger_repo.get_sum_deltas_for_product(product.id)

    assert ledger_sum == 2500

def test_update_transaction_change_price(groceries_service, logged_in_user):
    product = Product(
        user_id=logged_in_user.id, name="Apples", category=ProductCategoryEnum.FRUITS, net_weight=Decimal(500), unit_type=UnitEnum.G
    )
    db_session.add(product)
    db_session.flush()
    # txn1: 3 @ 500g -> ledger +1500
    # then net_weight changes to 300
    # txn1 update: price 2.50 -> 4.50, same qty
    txn1 = groceries_service.create_transaction({
        "product_id": product.id, "price_at_scan": "2.50", "quantity": 3,
    })
    db_session.flush()

    product.net_weight = Decimal(300)

    # update 2.50 -> 4.50
    txn = TransactionPatch(price_at_scan=4.50)
    groceries_service.update_transaction(txn, txn1.id)

    # correction row for latter 2 qty should use same net_weight as first 3:
    # original 1500 ledger + (new 2 @ same 500g each = 1000) = 2500
    ledger_sum = groceries_service.inventory_ledger_repo.get_sum_deltas_for_product(product.id)

    assert ledger_sum == 1500


#### Ensure _record_inventory_event helper affects ledger row AND qty_on_hand in sync
## incl create-row-when-missing branch and zero-delta skip
def test_record_inventory_event_skips_zero_delta(groceries_service, sample_products):
    dt = datetime(2026, 5, 5, tzinfo=ZoneInfo("UTC"))
    p1 = sample_products[0]
    groceries_service._record_inventory_event(
        product_id=p1.id, qty_delta=Decimal(0),
        event_type=InventoryLedgerEventTypeEnum.CORRECTION, entry_datetime=dt
    )
    # Assert no changes
    assert groceries_service.inventory_ledger_repo.get_all_for_product(p1.id) == []
    assert groceries_service.product_inventory_repo.get_by_product_id(p1.id) is None

def test_thing(groceries_service, sample_products):
    p1, _ = sample_products
    # PURCHASE in - p1 up 3 * 500g = 1500g
    txn = groceries_service.create_transaction({
        "product_id": p1.id, "price_at_scan": "2.50", "quantity": 3,
    })
    # CONSUMPTION out (ensure also valid cook)
    # p1 down 500g -> 1000g on hand now, -500g to ledger.
    new_recipe = RecipeCreate(
        name = "Test Recipe",
        yields = Decimal(200),
        yields_units = UnitEnum.G,
        ingredients = [
            RecipeIngredientCreate(product_id=p1.id, amount_value=Decimal(500), amount_units=UnitEnum.G),
        ]
    )
    recipe = groceries_service.create_recipe(new_recipe)
    db_session.flush()
    dt = datetime(2026, 5, 5, tzinfo=ZoneInfo("UTC"))
    groceries_service.cook_recipe(recipe.id, MealEnum.LUNCH, dt)
    # Mutate net_weight
    p1.net_weight = Decimal(1) # from 500g

    # CORRECTION - should use recovered per-unit not mutated weight
    # p1 +2 @ recovered 500g -> +1000g to ledger, 2000g on hand
    txn_patch = TransactionPatch(quantity=5) # 3 -> 5
    groceries_service.update_transaction(txn_patch, txn.id)

    # CORRECTION - must negate the linked sum
    # 1500 (original 3@500g) + 1000 (added 2@500g) = 2500
    # -2500g to ledger, on hand is now -500
    groceries_service.delete_transaction(txn.id)

    expected = -500

    inv = groceries_service.product_inventory_repo.get_by_product_id(p1.id)
    assert inv.qty_on_hand == groceries_service.inventory_ledger_repo.get_sum_deltas_for_product(p1.id)
    assert inv.qty_on_hand == expected


### all above tests ledger


## TEST: cook_recipe
def test_cook_recipe_works(groceries_service, sample_products):
    p1, p2 = sample_products
    new_recipe = RecipeCreate(
        name = "Test Recipe",
        yields = Decimal(200),
        yields_units = UnitEnum.G,
        ingredients = [
            RecipeIngredientCreate(product_id=p1.id, amount_value=Decimal(500), amount_units=UnitEnum.G),
            RecipeIngredientCreate(product_id=p2.id, amount_value=Decimal(600), amount_units=UnitEnum.G),
            # RecipeIngredientCreate(product_id=p3.id, amount_value=Decimal(200), amount_units=UnitEnum.G),
        ]
    )
    recipe = groceries_service.create_recipe(new_recipe)
    # Ensure we have stock
    # p1 net_weight = 500g -> need   1
    # p2 net_weight = 700g -> need > 1
    groceries_service.create_transaction({
        "product_id": p1.id, "price_at_scan": "2.50", "quantity": 1,
    })
    groceries_service.create_transaction({
        "product_id": p2.id, "price_at_scan": "2.50", "quantity": 1,
    })
    db_session.flush()

    # 2. Call cook_recipe
    tz_obj = ZoneInfo("UTC")
    entry_dt = datetime(2026, 5, 5, tzinfo=tz_obj)
    groceries_service.cook_recipe(recipe.id, MealEnum.LUNCH, entry_dt)

    # 3. nutrition log made
    nutrition_logs = groceries_service.nutrition_log_repo.get_all()
    # find log with matching dt?
    match = next(x for x in nutrition_logs if x.entry_datetime == entry_dt)
    assert match

    # 4. ledger consumption events made
    ledgers = groceries_service.inventory_ledger_repo.get_all_for_product(p1.id)
    # should be down 50g as most recent?
    match = next(x for x in ledgers if x.qty_delta == -500)
    assert match

    # 5. prod inventory qty_on_hand should be -50?
    inv = groceries_service.product_inventory_repo.get_by_product_id(p1.id)
    assert inv.qty_on_hand == 0

def test_cook_recipe_insufficient_stock(groceries_service, sample_products):
    p1, p2 = sample_products
    new_recipe = RecipeCreate(
        name = "Test Recipe",
        yields = Decimal(200),
        yields_units = UnitEnum.G,
        ingredients = [
            RecipeIngredientCreate(product_id=p1.id, amount_value=Decimal(700), amount_units=UnitEnum.G),
            RecipeIngredientCreate(product_id=p2.id, amount_value=Decimal(600), amount_units=UnitEnum.G),
        ]
    )
    recipe = groceries_service.create_recipe(new_recipe)
    # Ensure we have stock
    # p1 net_weight = 500g -> need   2 but have only 1!
    # p2 net_weight = 700g -> need > 1
    groceries_service.create_transaction({
        "product_id": p1.id, "price_at_scan": "2.50", "quantity": 1,
    })
    groceries_service.create_transaction({
        "product_id": p2.id, "price_at_scan": "2.50", "quantity": 1,
    })
    db_session.flush()

    # 2. Call cook_recipe
    tz_obj = ZoneInfo("UTC")
    entry_dt = datetime(2026, 5, 5, tzinfo=tz_obj)
    with pytest.raises(ServiceError, match="Not enough ingredients"):
        groceries_service.cook_recipe(recipe.id, MealEnum.LUNCH, entry_dt)
