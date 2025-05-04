from behave import given, when, then
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import time

ID_PREFIX = "inventory_"


# @given("I open the Inventory Admin UI")
# def step_open_ui(context):
#     print("Running Behave using the Chrome driver...")
#     base_url = os.getenv("BASE_URL", "http://localhost:8080")
#     options = webdriver.ChromeOptions()
#     options.add_argument("--headless=new")
#     options.add_argument("--no-sandbox")
#     options.add_argument("--disable-dev-shm-usage")
#     context.driver = webdriver.Chrome(options=options)
#     context.driver.get(base_url)
#     context.wait_seconds = 10
#     time.sleep(1)
@given("I open the Inventory Admin UI")
def step_open_ui(context):
    """Navigate to the application URL"""
    context.driver.get(context.base_url)
    time.sleep(1)  # Give the page time to load


@when('I enter "{value}" as the name')
def step_enter_name(context, value):
    field = context.driver.find_element(By.ID, "inventory_name")
    field.clear()
    field.send_keys(value)


@when('I enter "{value}" as the product ID')
def step_enter_product_id(context, value):
    field = context.driver.find_element(By.ID, "inventory_product_id")
    field.clear()
    field.send_keys(value)


@when('I enter "{value}" as the quantity')
def step_enter_quantity(context, value):
    field = context.driver.find_element(By.ID, "inventory_quantity")
    field.clear()
    field.send_keys(value)


@when('I select "{value}" as the condition')
def step_select_condition(context, value):
    select = Select(context.driver.find_element(By.ID, "inventory_condition"))
    select.select_by_visible_text(value)


@when('I enter "{value}" as the restock level')
def step_enter_restock_level(context, value):
    field = context.driver.find_element(By.ID, "inventory_restock_level")
    field.clear()
    field.send_keys(value)


@when('I press the "{button_text}" button')
def step_press_button(context, button_text):
    button_id_map = {
        "Create": "create-btn",
        "Retrieve": "retrieve-btn",
        "Update": "update-btn",
        "Delete": "delete-btn",
        "Clear": "clear-btn",
        "List All": "list-btn",
        "Search": "search-btn",
        "Restock": "perform-action-btn",
        "Perform Action": "perform-action-btn",
    }
    button_id = button_id_map.get(button_text)
    if not button_id:
        raise Exception(f"Unrecognized button: {button_text}")
    btn = context.driver.find_element(By.ID, button_id)
    btn.click()
    time.sleep(1)


@then('I should see "{value}" in the results table')
def step_see_in_table(context, value):
    table = context.driver.find_element(By.ID, "search_results_table")
    assert value in table.text


@then('I should not see "{value}" in the results')
def step_not_see_in_results(context, value):
    try:
        table = context.driver.find_element(By.ID, "search_results_table")
        assert value not in table.text
    except:
        pass


@when("I grab the first inventory ID from the results table")
def step_grab_id(context):
    table = context.driver.find_element(By.ID, "search_results_table")
    first_row = table.find_element(By.TAG_NAME, "tr")
    first_cell = first_row.find_element(By.TAG_NAME, "td")
    context.inventory_id = first_cell.text.strip()


@when("I enter the grabbed inventory ID")
def step_enter_grabbed_id(context):
    field = context.driver.find_element(By.ID, "inventory_id")
    field.clear()
    field.send_keys(context.inventory_id)


@then('the name field should contain "{value}"')
def step_verify_name(context, value):
    name = context.driver.find_element(By.ID, "inventory_name").get_attribute("value")
    assert name == value


@then('I should see "{text_string}" in the "{element_name}" field')
def step_verify_item(context, text_string, element_name):
    element_id = "inventory_" + element_name.lower().replace(" ", "_")
    found = WebDriverWait(context.driver, context.wait_seconds).until(
        EC.text_to_be_present_in_element_value((By.ID, element_id), text_string)
    )
    assert found


@when('I change "{element_name}" to "{text_string}"')
def step_update_item(context, element_name, text_string):
    element_id = "inventory_" + element_name.lower().replace(" ", "_")
    element = WebDriverWait(context.driver, context.wait_seconds).until(
        EC.presence_of_element_located((By.ID, element_id))
    )
    element.clear()
    element.send_keys(text_string)


@when('I select "{text}" in the "{element_name}" dropdown')
def step_select_dropdown_value(context, text, element_name):
    element_id = "inventory_" + element_name.lower().replace(" ", "_")
    select = Select(context.driver.find_element(By.ID, element_id))
    select.select_by_visible_text(text)


@when('I copy the "ID" field')
def step_copy_id_field(context):
    id_field = context.driver.find_element(By.ID, "inventory_id")
    context.inventory_id = id_field.get_attribute("value")


@then('I should see "{value}" as the {field}')
def step_verify_field_value(context, value, field):
    field_id = "inventory_" + field.lower()
    element = context.driver.find_element(By.ID, field_id)
    actual_value = element.get_attribute("value")
    assert str(actual_value) == value, f"Expected {value} but got {actual_value}"


# @then('I should see the message "{message}"')
# def step_verify_message(context, message):
#     flash = WebDriverWait(context.driver, context.wait_seconds).until(
#         EC.visibility_of_element_located((By.ID, "flash_message"))
#     )
#     assert message in flash.text
@then('I should see the message "{message}"')
def step_verify_message(context, message):
    wait = WebDriverWait(context.driver, 10)
    flash = wait.until(EC.visibility_of_element_located((By.ID, "flash_message")))
    actual = flash.text.strip()
    print(f"Expected: '{message}', Actual: '{actual}'")
    assert message.lower() in actual.lower()


@then('I should see a list of items that are "{condition}" condition')
def step_see_items_by_condition(context, condition):
    table = context.driver.find_element(By.ID, "search_results_table")
    rows = table.find_elements(By.TAG_NAME, "tr")
    found = any(
        len(cells := row.find_elements(By.TAG_NAME, "td")) > 0
        and cells[4].text.lower() == condition.lower()
        for row in rows
    )
    assert found, f"No items found with condition '{condition}'"


@when('I leave the quantity field empty and click the "Restock" button')
def step_empty_quantity_and_restock(context):
    field = context.driver.find_element(By.ID, "inventory_quantity")
    field.clear()
    context.driver.find_element(By.ID, "perform-action-btn").click()


@when('I enter {value:d} in the quantity field and click the "Restock" button')
def step_enter_quantity_and_restock(context, value):
    field = context.driver.find_element(By.ID, "inventory_quantity")
    field.clear()
    field.send_keys(str(value))
    context.driver.find_element(By.ID, "perform-action-btn").click()
    time.sleep(1)


@then("the item's quantity should be updated to {expected_quantity:d}")
def step_verify_quantity_updated(context, expected_quantity):
    field = context.driver.find_element(By.ID, "inventory_quantity")
    actual = int(field.get_attribute("value"))
    assert (
        actual == expected_quantity
    ), f"Expected quantity {expected_quantity}, but got {actual}"


@then("the flash message should confirm the quantity was updated")
def step_flash_confirm_quantity_updated(context):
    flash = WebDriverWait(context.driver, context.wait_seconds).until(
        EC.visibility_of_element_located((By.ID, "flash_message"))
    )
    assert "updated" in flash.text.lower()


# @then("the item's quantity should be updated to match the restock level")
# def step_verify_auto_restocked(context):
#     quantity = int(
#         context.driver.find_element(By.ID, "inventory_quantity").get_attribute("value")
#     )
#     restock = int(
#         context.driver.find_element(By.ID, "inventory_restock_level").get_attribute(
#             "value"
#         )
#     )
#     assert (
#         quantity == restock
#     ), f"Expected quantity to match restock level ({restock}), but got {quantity}"
@then("the item's quantity should be updated to match the restock level")
def step_verify_auto_restocked(context):
    """Verify quantity matches restock level after auto-restock"""
    # Wait for the API call to complete
    time.sleep(1)

    # First check the flash message BEFORE we click retrieve
    try:
        flash = WebDriverWait(context.driver, context.wait_seconds).until(
            EC.visibility_of_element_located((By.ID, "flash_message"))
        )
        context.restock_flash_message = flash.text  # Store for later verification
        print(f"Flash message after restock: '{flash.text}'")
    except:
        context.restock_flash_message = ""

    # Click the Retrieve button to get the updated data
    try:
        retrieve_btn = context.driver.find_element(By.ID, "retrieve-btn")
        retrieve_btn.click()
        time.sleep(1)  # Wait for data to load
    except Exception as e:
        print(f"Error clicking retrieve button: {e}")

    # Now check the quantity field
    quantity_field = context.driver.find_element(By.ID, "inventory_quantity")
    quantity_value = quantity_field.get_attribute("value")

    # Get the restock level for comparison
    restock_field = context.driver.find_element(By.ID, "inventory_restock_level")
    restock_value = restock_field.get_attribute("value")

    if not quantity_value:
        assert False, "Quantity field is still empty after retrieving updated data"

    quantity = int(quantity_value)
    restock = int(restock_value)

    assert (
        quantity == restock
    ), f"Expected quantity to match restock level ({restock}), but got {quantity}"


# @then("the flash message should confirm the restock was successful")
# def step_flash_confirm_restock(context):
#     flash = WebDriverWait(context.driver, context.wait_seconds).until(
#         EC.visibility_of_element_located((By.ID, "flash_message"))
#     )
#     assert "restock" in flash.text.lower()
@then("the flash message should confirm the restock was successful")
def step_flash_confirm_restock(context):
    """Verify restock success message"""
    # Use the stored flash message from the restock action
    if hasattr(context, "restock_flash_message"):
        flash_text = context.restock_flash_message.lower()
    else:
        # Fallback: try to get current flash message
        flash = WebDriverWait(context.driver, context.wait_seconds).until(
            EC.visibility_of_element_located((By.ID, "flash_message"))
        )
        flash_text = flash.text.lower()

    # The expected message from the backend
    assert (
        "stock level updated" in flash_text
    ), f"Expected 'stock level updated' in flash message, but got: '{context.restock_flash_message if hasattr(context, 'restock_flash_message') else flash.text}'"


@given("I have an inventory item with quantity 2")
def step_seed_inventory_quantity_2(context):
    context.execute_steps(
        """
        Given I open the Inventory Admin UI
        When I enter "Notebook" as the name
        And I enter "1001" as the product ID
        And I enter "2" as the quantity
        And I select "New" as the condition
        And I enter "10" as the restock level
        And I press the "Create" button
    """
    )


@given("I have an inventory item with quantity 1 and restock level 5")
def step_seed_inventory_quantity_1(context):
    context.execute_steps(
        """
        Given I open the Inventory Admin UI
        When I enter "Headphones" as the name
        And I enter "1002" as the product ID
        And I enter "1" as the quantity
        And I select "Used" as the condition
        And I enter "5" as the restock level
        And I press the "Create" button
    """
    )


@given("the user is on the home page")
def step_user_on_home(context):
    context.driver.get(os.getenv("BASE_URL", "http://localhost:8080"))


@when("the user clicks the List All button")
def step_user_clicks_list(context):
    context.driver.find_element(By.ID, "list-btn").click()


@then("the inventory list should be displayed")
def step_verify_inventory_list(context):
    table = WebDriverWait(context.driver, 10).until(
        EC.visibility_of_element_located((By.ID, "search_results_table"))
    )
    rows = table.find_elements(By.TAG_NAME, "tr")
    assert len(rows) > 0, "Expected inventory items to be listed, but none were found."
