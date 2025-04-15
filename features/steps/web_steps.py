from behave import given, when, then
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
import os
import time


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
    btn = context.driver.find_element(By.XPATH, f'//button[text()="{button_text}"]')
    btn.click()
    time.sleep(1)


@then('I should see "{value}" in the results table')
def step_see_in_table(context, value):
    table = context.driver.find_element(By.ID, "search_results_table")
    assert value in table.text


@when('I grab the first inventory ID from the results table')
def step_grab_id(context):
    table = context.driver.find_element(By.ID, "search_results_table")
    first_row = table.find_element(By.TAG_NAME, "tr")
    first_cell = first_row.find_element(By.TAG_NAME, "td")
    inventory_id = first_cell.text.strip()
    context.inventory_id = inventory_id
    print("DEBUG >>> Grabbed ID:", inventory_id)


@when('I enter the grabbed inventory ID')
def step_enter_grabbed_id(context):
    field = context.driver.find_element(By.ID, "inventory_id")
    field.clear()
    field.send_keys(context.inventory_id)


@then('the name field should contain "{value}"')
def step_verify_name(context, value):
    name = context.driver.find_element(By.ID, "inventory_name").get_attribute("value")
    print("DEBUG >>> Name field contains:", name)
    assert name == value
