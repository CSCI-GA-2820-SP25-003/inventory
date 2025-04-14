from behave import given
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os

@given("I open the Inventory Admin UI")
def step_open_ui(context):
    options = Options()
    options.headless = True  # Run without opening a browser window
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    # IMPORTANT: Set the correct binary location if not automatically found
    options.binary_location = "/usr/bin/google-chrome"  # or "/snap/bin/chromium" if using snap

    context.driver = webdriver.Chrome(options=options)
    
    base_url = os.getenv("BASE_URL", "http://localhost:8080/ui")
    context.driver.get(base_url)
