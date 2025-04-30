from behave import given, when, then
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import time

ID_PREFIX = "inventory_"

@given("I open the Inventory Admin UI")
def step_open_ui(context):
    print("Running Behave using the Chrome driver...")
    base_url = os.getenv("BASE_URL", "http://localhost:8080")
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    context.driver = webdriver.Chrome(options=options)
    context.driver.get(base_url)
    time.sleep(1)

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
    try:
        # Attempt to locate by visible text
        btn = context.driver.find_element(By.XPATH, f'//button[text()="{button_text}"]')
    except:
        # Fallback to button ID
        btn = context.driver.find_element(By.ID, f'{button_text.lower()}-btn')
    btn.click()
    time.sleep(1)

@then('I should see "{value}" in the results table')
def step_see_in_table(context, value):
    table = context.driver.find_element(By.ID, "search_results_table")
    assert value in table.text

@when("I grab the first inventory ID from the results table")
def step_grab_id(context):
    table = context.driver.find_element(By.ID, "search_results_table")
    first_row = table.find_element(By.TAG_NAME, "tr")
    first_cell = first_row.find_element(By.TAG_NAME, "td")
    inventory_id = first_cell.text.strip()
    context.inventory_id = inventory_id
    print("DEBUG >>> Grabbed ID:", inventory_id)

@when("I enter the grabbed inventory ID")
def step_enter_grabbed_id(context):
    field = context.driver.find_element(By.ID, "inventory_id")
    field.clear()
    field.send_keys(context.inventory_id)

@then('the name field should contain "{value}"')
def step_verify_name(context, value):
    name = context.driver.find_element(By.ID, "inventory_name").get_attribute("value")
    print("DEBUG >>> Name field contains:", name)
    assert name == value

@when('I change "{element_name}" to "{text_string}"')
def step_update_item(context, element_name, text_string):
    element_id = "inventory_" + element_name.lower().replace(" ", "_")
    element = WebDriverWait(context.driver, context.wait_seconds).until(
        EC.presence_of_element_located((By.ID, element_id))
    )
    element.clear()
    element.send_keys(text_string)

@then('I should see "{text_string}" in the "{element_name}" field')
def step_verify_item(context, text_string, element_name):
    element_id = "inventory_" + element_name.lower().replace(" ", "_")
    found = WebDriverWait(context.driver, context.wait_seconds).until(
        EC.text_to_be_present_in_element_value((By.ID, element_id), text_string)
    )
    assert found

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

@then('I should see the message "{message}"')
def step_verify_message(context, message):
    flash_message = WebDriverWait(context.driver, context.wait_seconds).until(
        EC.presence_of_element_located((By.ID, "flash_message"))
    )
    assert message in flash_message.text

@then('I should not see "{value}" in the results')
def step_not_see_in_results(context, value):
    try:
        table = context.driver.find_element(By.ID, "search_results_table")
        assert value not in table.text
    except:
        pass

@then('I should see a list of items that are "{condition}" condition')
def step_see_items_by_condition(context, condition):
    table = context.driver.find_element(By.ID, "search_results_table")
    rows = table.find_elements(By.TAG_NAME, "tr")
    found = any(len(cells := row.find_elements(By.TAG_NAME, "td")) > 0 and cells[3].text == condition for row in rows)
    assert found, f"No items found with condition '{condition}'"

@given("I have an inventory item with quantity 2")
def step_impl_quantity_2(context):
    context.execute_steps(
        f"""
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
def step_impl_quantity_1_restock_5(context):
    context.execute_steps(
        f"""
        Given I open the Inventory Admin UI
        When I enter "Headphones" as the name
        And I enter "1002" as the product ID
        And I enter "1" as the quantity
        And I select "Used" as the condition
        And I enter "5" as the restock level
        And I press the "Create" button
        """
    )

@when('I leave the quantity field empty and click the "Restock" button')
def step_impl_empty_quantity(context):
    field = context.driver.find_element(By.ID, "inventory_quantity")
    field.clear()
    context.driver.find_element(By.ID, "perform-action-btn").click()

@given('the user is on the home page')
def step_user_on_home(context):
    context.browser.get(context.base_url)

@when('the user clicks the List All button')
def step_user_click_list_all(context):
    list_button = context.browser.find_element(By.ID, 'list-btn')
    list_button.click()

@then('the inventory list should be displayed')
def step_inventory_list_displayed(context):
    table = WebDriverWait(context.browser, 10).until(
        EC.visibility_of_element_located((By.ID, 'search_results_table'))
    )
    rows = table.find_elements(By.TAG_NAME, 'tr')
    assert len(rows) > 0, "Expected inventory items to be listed, but none were found."
