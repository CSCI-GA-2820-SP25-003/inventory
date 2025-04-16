from behave import then, given
from selenium.webdriver.common.by import By
import requests
import os

@then('I should see the title "Inventory Demo RESTful Service"')
def step_see_title(context):
    assert "Inventory Demo RESTful Service" in context.driver.title

@given("the following inventory items")
def step_seed_inventory(context):
    """Delete all inventory items and create new ones from table"""
    base_url = os.getenv("BASE_URL", "http://localhost:8080/inventory")

    # Clear existing inventory (optional: only if API supports it)
    response = requests.get(f"{base_url}/api/inventory")
    if response.status_code == 200:
        for item in response.json():
            requests.delete(f"{base_url}/api/inventory/{item['id']}")

    # Create inventory items from table
    for row in context.table:
        payload = {
            "name": row["name"],
            "product_id": int(row["product_id"]),
            "quantity": int(row["quantity"]),
            "condition": row["condition"],
            "restock_level": int(row["restock_level"]),
        }
        resp = requests.post(f"{base_url}/api/inventory", json=payload)
        assert resp.status_code == 201
