from behave import then
from selenium.webdriver.common.by import By

@then('I should see the title "Inventory Demo RESTful Service"')
def step_see_title(context):
    assert "Inventory Demo RESTful Service" in context.driver.title
