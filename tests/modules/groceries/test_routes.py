



def test_groceries_dashboard(client):
    response = client.get("/groceries/")
    assert response.status_code == 200
    # assert b"Groceries" in response.data ADD THIS CHECK WHEN WE ADD LANGUAGE TOGGLE TO EN DE

def test_add_product_page(client):
    response = client.get("/groceries/add_product")
    assert response.status_code == 200