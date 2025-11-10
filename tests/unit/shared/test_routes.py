

def test_all_expected_routes_registered(app):
    """Verify routes are registered, don't even hit them"""
    
    expected_routes = [
        '/api/tasks/tasks/<int:item_id>',
        '/api/habits/habits/<int:item_id>',
        '/api/groceries/products/<int:item_id>',
        '/api/groceries/shopping-lists/items',
        # ... etc
    ]
    
    registered_routes = [rule.rule for rule in app.url_map.iter_rules()]
    
    for route in expected_routes:
        assert route in registered_routes, f"Route {route} not registered!"

def test_print_all_registered_routes(app):
    """Helper to see what routes you actually have"""
    print("\nAll registered routes:")
    for rule in app.url_map.iter_rules():
        # if '/api/' in rule.rule:  # Only show API routes
        methods = ','.join(rule.methods - {'HEAD', 'OPTIONS'})
        print(f"  {methods:20} {rule.rule}")