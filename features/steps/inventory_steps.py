from behave import then
from selenium.webdriver.common.by import By

@then('I should see the title "Inventory Shop"')
def step_see_title(context):
    assert "Inventory Shop" in context.driver.title
    context.driver.quit()
