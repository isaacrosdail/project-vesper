

# ---- Products ----
def test_create_product_valid(authenticated_client):
    resp = authenticated_client.post("/api/groceries/products", json={
        "name": "Oats", "category": "grains",
        "net_weight": 500, "unit_type": "g",
    })
    assert resp.status_code == 201

def test_create_product_invalid(authenticated_client):
    resp = authenticated_client.post("/api/groceries/products", json={
        "name": "", "category": "not_a_category",
    })
    assert resp.status_code == 400

def test_patch_product_valid(authenticated_client):
    create = authenticated_client.post("/api/groceries/products", json={
        "name": "Oats", "category": "grains",
        "net_weight": 500, "unit_type": "g",
    })
    product_id = create.json["data"]["id"]
    resp = authenticated_client.patch(f"/api/groceries/products/{product_id}", json={
        "name": "Rolled Oats"
    })
    assert resp.status_code == 200
    assert resp.json["data"]["name"] == "Rolled Oats"

def test_patch_product_invalid(authenticated_client):
    create = authenticated_client.post("/api/groceries/products", json={
        "name": "Oats", "category": "grains",
        "net_weight": 500, "unit_type": "g",
    })
    product_id = create.json["data"]["id"]
    resp = authenticated_client.patch(f"/api/groceries/products/{product_id}", json={
        "net_weight": -100
    })
    assert resp.status_code == 400


# ---- Recipes ----
def test_create_recipe_valid(authenticated_client):
    # Need a product first
    prod = authenticated_client.post("/api/groceries/products", json={
        "name": "Oats", "category": "grains",
        "net_weight": 500, "unit_type": "g",
    })
    product_id = prod.json["data"]["id"]
    resp = authenticated_client.post("/api/groceries/recipes", json={
        "name": "Oatmeal",
        "yields": 1,
        "yields_units": "ea",
        "ingredients": [{
            "product_id": product_id,
            "amount_value": 100,
            "amount_units": "g",
        }]
    })
    assert resp.status_code == 201

def test_create_recipe_invalid(authenticated_client):
    resp = authenticated_client.post("/api/groceries/recipes", json={
        "name": "",
        "yields": -1,
    })
    assert resp.status_code == 400


def test_valid_product_nutrition(authenticated_client):
    resp = authenticated_client.post("/api/groceries/products",
json={
        "name": "Oats", "category": "grains",
        "net_weight": 500, "unit_type": "g",
        "calories_per_100g": 389,
        "protein_per_100g": 16.9,
        "fat_per_100g": 6.9,
        "carbs_per_100g": 66.3,
    })
    assert resp.status_code == 201

def test_fat_subtypes_exceed_total(authenticated_client):
    resp = authenticated_client.post("/api/groceries/products", json={
        "name": "Bad Fat", "category": "snacks",
        "net_weight": 100, "unit_type": "g",
        "fat_per_100g": 5,
        "fat_sat_per_100g": 3,
        "fat_mono_per_100g": 2,
        "fat_poly_per_100g": 2,  # total 7 > 5
    })
    assert resp.status_code == 400

def test_calories_mismatch_macros(authenticated_client):
    resp = authenticated_client.post("/api/groceries/products", json={
        "name": "Wrong Cals", "category": "snacks",
        "net_weight": 100, "unit_type": "g",
        "calories_per_100g": 100,
        "protein_per_100g": 50,  # 200 cal from protein alone
        "fat_per_100g": 20,     # 180 cal from fat
        "carbs_per_100g": 30,   # 120 cal from carbs = 500 total vs 100 stated
    })
    assert resp.status_code == 400


# ---- Groceries ----
def test_create_product(authenticated_client):
    response = authenticated_client.post("/api/groceries/products", json={
        "name": "Oats",
        "category": "grains",
        "net_weight": 500,
        "unit_type": "g",
    })
    assert response.status_code == 201




def test_recipe_with_ingredients_roundtrip(authenticated_client):
    """Create product, then recipe with that product as ingredient."""
    # Need a product first
    prod = authenticated_client.post("/api/groceries/products", json={
        "name": "Oats", "category": "grains",
        "net_weight": 500, "unit_type": "g",
    })
    product_id = prod.json["data"]["id"]

    # Create recipe with ingredient
    recipe = authenticated_client.post("/api/groceries/recipes", json={
        "name": "Oatmeal",
        "yields": 1,
        "yields_units": "ea",
        "ingredients": [{
            "product_id": product_id,
            "amount_value": 100,
            "amount_units": "g",
        }]
    })
    assert recipe.status_code == 201
    assert len(recipe.json["data"]["ingredients"]) == 1
    assert recipe.json["data"]["ingredients"][0]["product_name"] == "Oats"
