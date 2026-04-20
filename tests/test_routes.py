
def test_patch_task_pillars(authenticated_client):
    create = authenticated_client.post('/api/tasks/tasks', json={
        'name': 'Test task', 'priority': 'low',
    })
    task_id = create.json['data']['id']
    print(task_id)

    # Use actual pillar IDs from the seeded data
    response = authenticated_client.patch(f'/api/tasks/tasks/{task_id}', json={
        'pillar_ids': [1, 2]  # might need to adjust based on actual IDs
    })
    assert response.status_code == 200
    assert len(response.json['data']['pillars']) == 2


def test_patch_task_invalid_priority(authenticated_client):
    response = authenticated_client.patch('/api/tasks/tasks/1', json={
        'priority': 'banana'
    })
    assert response.status_code == 400

# ---- Tasks ----
def test_create_task(authenticated_client):
    response = authenticated_client.post('/api/tasks/tasks', json={
        'name': 'Test task',
        'priority': 'medium',
    })
    assert response.status_code == 201
    assert response.json['data']['name'] == 'Test task'

def test_get_all_tasks(authenticated_client):
    # Create one first
    authenticated_client.post('/api/tasks/tasks', json={
        'name': 'Task 1', 'priority': 'low',
    })
    response = authenticated_client.get('/api/tasks/tasks')
    assert response.status_code == 200
    assert len(response.json['data']) >= 1

def test_patch_task(authenticated_client):
    # Create then patch
    create = authenticated_client.post('/api/tasks/tasks', json={
        'name': 'Original', 'priority': 'low',
    })
    task_id = create.json['data']['id']
    response = authenticated_client.patch(f'/api/tasks/tasks/{task_id}', json={
        'name': 'Updated'
    })
    assert response.status_code == 200
    assert response.json['data']['name'] == 'Updated'

def test_delete_task(authenticated_client):
    create = authenticated_client.post('/api/tasks/tasks', json={
        'name': 'To delete', 'priority': 'low',
    })
    task_id = create.json['data']['id']
    response = authenticated_client.delete(f'/api/tasks/tasks/{task_id}')
    assert response.status_code == 200

# ---- Habits ----
def test_create_habit(authenticated_client):
    response = authenticated_client.post('/api/habits/habits', json={
        'name': 'Morning workout', 'target_frequency': 4
    })
    assert response.status_code == 201

# ---- Metrics ----
def test_create_daily_metrics(authenticated_client):
    response = authenticated_client.post('/api/metrics/daily_metrics', json={
        'entry_date': '2026-03-20',
        'steps': 8000,
        'calories': 2100,
    })
    assert response.status_code == 201

# ---- Groceries ----
def test_create_product(authenticated_client):
    response = authenticated_client.post('/api/groceries/products', json={
        'name': 'Oats',
        'category': 'grains',
        'net_weight': 500,
        'unit_type': 'g',
    })
    assert response.status_code == 201


def test_create_task_with_pillars_roundtrip(authenticated_client):
      """Create task, add pillars, fetch it back, verify pillars persist."""
      create = authenticated_client.post('/api/tasks/tasks', json={
          'name': 'Pillar test', 'priority': 'high',
      })
      task_id = create.json['data']['id']
      # Patch pillars in
      resp1 = authenticated_client.patch(f'/api/tasks/tasks/{task_id}', json={
          'pillar_ids': [1, 2]
      })
      print(resp1.json)

      # Fetch all and find our task
      get_all = authenticated_client.get('/api/tasks/tasks')
      task = next(t for t in get_all.json['data'] if t['id'] == task_id)
      assert len(task['pillars']) == 2


def test_toggle_complete_roundtrip(authenticated_client):
    """Complete a task, verify it sticks."""
    create = authenticated_client.post('/api/tasks/tasks', json={
        'name': 'Toggle test', 'priority': 'low',
    })
    task_id = create.json['data']['id']
    # print(task_id, create.json)
    assert create.json['data']['is_done'] == False
    # Complete it
    resp2 = authenticated_client.patch(f'/api/tasks/tasks/{task_id}', json={
        'completed_at': '2026-03-20T12:00:00Z'
    })
    # print(resp2.json)

    # Fetch and verify
    task = authenticated_client.get(f'/api/tasks/tasks/{task_id}')
    print(task.json)
    # task = next(t for t in get_all.json['data'] if t['id'] == task_id)
    assert task.json['data']['is_done'] == True


def test_uncomplete_task(authenticated_client):
    """Complete then uncomplete a task."""
    create = authenticated_client.post('/api/tasks/tasks', json={
        'name': 'Uncomplete test', 'priority': 'low',
    })
    task_id = create.json['data']['id']

    # Complete
    authenticated_client.patch(f'/api/tasks/tasks/{task_id}', json={
        'completed_at': '2026-03-20T12:00:00Z'
    })
    # Uncomplete
    authenticated_client.patch(f'/api/tasks/tasks/{task_id}', json={
        'completed_at': None
    })

    get_all = authenticated_client.get('/api/tasks/tasks')
    task = next(t for t in get_all.json['data'] if t['id'] == task_id)
    assert task['is_done'] == False


def test_remove_pillars(authenticated_client):
    """Add pillars then remove them."""
    create = authenticated_client.post('/api/tasks/tasks', json={
        'name': 'Remove pillars test', 'priority': 'low',
    })
    task_id = create.json['data']['id']

    # Add
    authenticated_client.patch(f'/api/tasks/tasks/{task_id}', json={
        'pillar_ids': '1,2'
    })
    # Remove (empty string = no pillars)
    authenticated_client.patch(f'/api/tasks/tasks/{task_id}', json={
        'pillar_ids': ''
    })

    get_all = authenticated_client.get('/api/tasks/tasks')
    task = next(t for t in get_all.json['data'] if t['id'] == task_id)
    assert len(task['pillars']) == 0


def test_recipe_with_ingredients_roundtrip(authenticated_client):
    """Create product, then recipe with that product as ingredient."""
    # Need a product first
    prod = authenticated_client.post('/api/groceries/products', json={
        'name': 'Oats', 'category': 'grains',
        'net_weight': 500, 'unit_type': 'g',
    })
    product_id = prod.json['data']['id']
    print(product_id)

    # Create recipe with ingredient
    recipe = authenticated_client.post('/api/groceries/recipes', json={
        'name': 'Oatmeal',
        'yields': 1,
        'yields_units': 'ea',
        'ingredients': [{
            'product_id': product_id,
            'amount_value': 100,
            'amount_units': 'g',
        }]
    })
    print(recipe.json)
    assert recipe.status_code == 201
    assert len(recipe.json['data']['ingredients']) == 1
    assert recipe.json['data']['ingredients'][0]['product_name'] == 'Oats'


def test_patch_only_updates_sent_fields(authenticated_client):
    """Patch name shouldn't wipe priority."""
    create = authenticated_client.post('/api/tasks/tasks', json={
        'name': 'Original', 'priority': 'high',
    })
    task_id = create.json['data']['id']

    # Only patch name
    authenticated_client.patch(f'/api/tasks/tasks/{task_id}', json={
        'name': 'Updated'
    })

    get_all = authenticated_client.get('/api/tasks/tasks')
    task = next(t for t in get_all.json['data'] if t['id'] == task_id)
    assert task['name'] == 'Updated'
    assert task['priority'] == 'high'  # should NOT be wiped


# def test_create_task_valid(authenticated_client):
#     resp = authenticated_client.post('/api/tasks/tasks', json={
#         'name': 'Test', 'priority': 'low'
#     })
#     assert resp.status_code == 201

# def test_create_task_invalid(authenticated_client):
#     resp = authenticated_client.post('/api/tasks/tasks', json={
#         'name': '', 'priority': 'banana'
#     })
#     assert resp.status_code == 400
#     assert resp.json['code'] == 'VALIDATION_ERROR'

# ● # ---- Tasks ----
def test_create_task_valid(authenticated_client):
    resp = authenticated_client.post('/api/tasks/tasks', json={
        'name': 'Test task', 'priority': 'low'
    })
    assert resp.status_code == 201

def test_create_task_invalid(authenticated_client):
    resp = authenticated_client.post('/api/tasks/tasks', json={
        'name': '', 'priority': 'banana'
    })
    assert resp.status_code == 400
    assert resp.json['code'] == 'VALIDATION_ERROR'

def test_patch_task_valid(authenticated_client):
    create = authenticated_client.post('/api/tasks/tasks', json={
        'name': 'Original', 'priority': 'low'
    })
    task_id = create.json['data']['id']
    resp = authenticated_client.patch(f'/api/tasks/tasks/{task_id}', json={
        'name': 'Updated'
    })
    assert resp.status_code == 200
    assert resp.json['data']['name'] == 'Updated'

def test_patch_task_invalid(authenticated_client):
    create = authenticated_client.post('/api/tasks/tasks', json={
        'name': 'Original', 'priority': 'low'
    })
    task_id = create.json['data']['id']
    resp = authenticated_client.patch(f'/api/tasks/tasks/{task_id}', json={
        'priority': 'banana'
    })
    assert resp.status_code == 400


# ---- Habits ----
def test_create_habit_valid(authenticated_client):
    resp = authenticated_client.post('/api/habits/habits', json={
        'name': 'Morning run', 'target_frequency': 7, 'is_promotable': 'on'
    })
    print(resp.json)
    assert resp.status_code == 201

def test_create_habit_invalid(authenticated_client):
    resp = authenticated_client.post('/api/habits/habits', json={
        'name': ''
    })
    assert resp.status_code == 400

def test_patch_habit_valid(authenticated_client):
    create = authenticated_client.post('/api/habits/habits', json={
        'name': 'Morning run', 'target_frequency': 7
    })
    print(f"create.json: {create.json}")
    habit_id = create.json['data']['id']
    print(habit_id)
    resp = authenticated_client.patch(f'/api/habits/habits/{habit_id}', json={
        'name': 'Evening run'
    })
    print(resp.json)
    assert resp.status_code == 200

def test_patch_habit_invalid(authenticated_client):
    create = authenticated_client.post('/api/habits/habits', json={
        'name': 'Morning run', 'target_frequency': 7
    })
    habit_id = create.json['data']['id']
    resp = authenticated_client.patch(f'/api/habits/habits/{habit_id}', json={
        'target_frequency': -5
    })
    assert resp.status_code == 400


# ---- Metrics ----
def test_create_metrics_valid(authenticated_client):
    resp = authenticated_client.post('/api/metrics/daily_metrics', json={
        'entry_date': '2026-03-20',
        'steps': 8000,
        'calories': 2100,
    })
    assert resp.status_code == 201

def test_create_metrics_invalid(authenticated_client):
    resp = authenticated_client.post('/api/metrics/daily_metrics', json={
        'steps': -500,
    })
    assert resp.status_code == 400

def test_patch_metrics_valid(authenticated_client):
    create = authenticated_client.post('/api/metrics/daily_metrics', json={
        'entry_date': '2026-03-20',
        'steps': 8000,
    })
    entry_id = create.json['data']['id']
    print(entry_id)
    resp = authenticated_client.patch(f'/api/metrics/daily_metrics/{entry_id}', json={
        'entry_date': '2026-03-20',
        'steps': 12000
    })
    print(resp.json)
    assert resp.status_code == 200

def test_patch_metrics_invalid(authenticated_client):
    create = authenticated_client.post('/api/metrics/daily_metrics', json={
        'entry_date': '2026-03-20',
        'steps': 8000,
    })
    entry_id = create.json['data']['id']
    resp = authenticated_client.patch(f'/api/metrics/daily_metrics/{entry_id}', json={
        'steps': -100
    })
    assert resp.status_code == 400


# ---- Time Tracking ----
def test_create_time_entry_valid(authenticated_client):
    resp = authenticated_client.post('/api/time_tracking/time_entries', json={
        'entry_date': '2026-03-20',
        'category': 'Work',
        'started_at': '09:00',
        'ended_at': '11:00',
    })
    assert resp.status_code == 201

def test_create_time_entry_invalid(authenticated_client):
    resp = authenticated_client.post('/api/time_tracking/time_entries', json={
        'category': '',
        'started_at': '09:00',
    })
    assert resp.status_code == 400

def test_patch_time_entry_valid(authenticated_client):
    create = authenticated_client.post('/api/time_tracking/time_entries', json={
        'entry_date': '2026-03-20',
        'category': 'Work',
        'started_at': '09:00',
        'ended_at': '11:00',
    })
    entry_id = create.json['data']['id']
    print(entry_id)
    resp = authenticated_client.patch(f'/api/time_tracking/time_entries/{entry_id}', json={
        'category': 'Deep Work'
    })
    assert resp.status_code == 200

def test_patch_time_entry_invalid(authenticated_client):
    create = authenticated_client.post('/api/time_tracking/time_entries', json={
        'entry_date': '2026-03-20',
        'category': 'Work',
        'started_at': '09:00',
        'ended_at': '11:00',
    })
    entry_id = create.json['data']['id']
    resp = authenticated_client.patch(f'/api/time_tracking/time_entries/{entry_id}', json={
        'started_at': 'not-a-time'
    })
    assert resp.status_code == 400


# ---- Products ----
def test_create_product_valid(authenticated_client):
    resp = authenticated_client.post('/api/groceries/products', json={
        'name': 'Oats', 'category': 'grains',
        'net_weight': 500, 'unit_type': 'g',
    })
    assert resp.status_code == 201

def test_create_product_invalid(authenticated_client):
    resp = authenticated_client.post('/api/groceries/products', json={
        'name': '', 'category': 'not_a_category',
    })
    assert resp.status_code == 400

def test_patch_product_valid(authenticated_client):
    create = authenticated_client.post('/api/groceries/products', json={
        'name': 'Oats', 'category': 'grains',
        'net_weight': 500, 'unit_type': 'g',
    })
    product_id = create.json['data']['id']
    resp = authenticated_client.patch(f'/api/groceries/products/{product_id}', json={
        'name': 'Rolled Oats'
    })
    assert resp.status_code == 200
    assert resp.json['data']['name'] == 'Rolled Oats'

def test_patch_product_invalid(authenticated_client):
    create = authenticated_client.post('/api/groceries/products', json={
        'name': 'Oats', 'category': 'grains',
        'net_weight': 500, 'unit_type': 'g',
    })
    product_id = create.json['data']['id']
    resp = authenticated_client.patch(f'/api/groceries/products/{product_id}', json={
        'net_weight': -100
    })
    assert resp.status_code == 400


# ---- Recipes ----
def test_create_recipe_valid(authenticated_client):
    # Need a product first
    prod = authenticated_client.post('/api/groceries/products', json={
        'name': 'Oats', 'category': 'grains',
        'net_weight': 500, 'unit_type': 'g',
    })
    product_id = prod.json['data']['id']
    resp = authenticated_client.post('/api/groceries/recipes', json={
        'name': 'Oatmeal',
        'yields': 1,
        'yields_units': 'ea',
        'ingredients': [{
            'product_id': product_id,
            'amount_value': 100,
            'amount_units': 'g',
        }]
    })
    print(resp.json)
    assert resp.status_code == 201

def test_create_recipe_invalid(authenticated_client):
    resp = authenticated_client.post('/api/groceries/recipes', json={
        'name': '',
        'yields': -1,
    })
    print(resp.json)
    assert resp.status_code == 400


def test_valid_product_nutrition(authenticated_client):
    resp = authenticated_client.post('/api/groceries/products',
json={
        'name': 'Oats', 'category': 'grains',
        'net_weight': 500, 'unit_type': 'g',
        'calories_per_100g': 389,
        'protein_per_100g': 16.9,
        'fat_per_100g': 6.9,
        'carbs_per_100g': 66.3,
    })
    assert resp.status_code == 201

def test_fat_subtypes_exceed_total(authenticated_client):
    resp = authenticated_client.post('/api/groceries/products', json={
        'name': 'Bad Fat', 'category': 'snacks',
        'net_weight': 100, 'unit_type': 'g',
        'fat_per_100g': 5,
        'fat_sat_per_100g': 3,
        'fat_mono_per_100g': 2,
        'fat_poly_per_100g': 2,  # total 7 > 5
    })
    assert resp.status_code == 400

def test_calories_mismatch_macros(authenticated_client):
    resp = authenticated_client.post('/api/groceries/products', json={
        'name': 'Wrong Cals', 'category': 'snacks',
        'net_weight': 100, 'unit_type': 'g',
        'calories_per_100g': 100,
        'protein_per_100g': 50,  # 200 cal from protein alone
        'fat_per_100g': 20,     # 180 cal from fat
        'carbs_per_100g': 30,   # 120 cal from carbs = 500 total vs 100 stated
    })
    assert resp.status_code == 400