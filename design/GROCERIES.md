
# Covers:
- InventoryLedger: append-only event ledger + derived ProductInventory cache (TODO)


## InventoryLedger stuff: March 13: Starting to track nutrition/intake, as well as keeping proper tabs on product inventory

Problem: The system records purchases, and now consumption per mealtime, but determining current stock requires
repeatedly recomputing totals from multiple tables (transactions/purchases - consumption). That approach becomes messy
as more actions will appear (recipes, waste, corrections) and makes "what changed when" difficult to reason about.

Design goal:
Represent inventory as a chronological sequence of immutable events so every change to our product stock is recorded
explicitly and clearly. Current stock should also be cheap to read, while the history of inventory state and analytics should
still be derivable.

Plan:
- InventoryEvent: append-only ledger entries with product_id, quantity_delta, event_type (ie, "purchase", "waste", "consumption"), and created_at.
    - Inserts are the only write operation. If inventory needs correction, we'd insert another event (eg 'correction +50') instead of editing an old row.

- Two new models:
    1. InventoryLedger: Source of truth; append-only, every inventory change gets a row. Put a composite (product_id, created_at) index because our
    primary access pattern is "all events for a given product in a given time range". Index pre-sorts by product_id first, then chronologically within
    each product.
    2. ProductInventory: Cache of the current state, derived from the ledger.


