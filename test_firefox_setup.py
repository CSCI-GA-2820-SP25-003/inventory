from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
import subprocess
import os

print("=== Firefox Setup Test ===")

# Check Firefox installation
print("\n1. Checking Firefox installation:")
try:
    result = subprocess.run(['which', 'firefox'], capture_output=True, text=True)
    print(f"firefox: {result.stdout.strip() if result.stdout else 'Not found'}")
    
    result = subprocess.run(['which', 'firefox-esr'], capture_output=True, text=True)
    print(f"firefox-esr: {result.stdout.strip() if result.stdout else 'Not found'}")
    
    result = subprocess.run(['firefox-esr', '--version'], capture_output=True, text=True)
    print(f"Firefox version: {result.stdout.strip()}")
except Exception as e:
    print(f"Error checking Firefox: {e}")

# Check GeckoDriver installation
print("\n2. Checking GeckoDriver installation:")
try:
    result = subprocess.run(['which', 'geckodriver'], capture_output=True, text=True)
    print(f"geckodriver: {result.stdout.strip() if result.stdout else 'Not found'}")
    
    result = subprocess.run(['geckodriver', '--version'], capture_output=True, text=True)
    print(f"GeckoDriver version: {result.stdout.strip()}")
except Exception as e:
    print(f"Error checking GeckoDriver: {e}")

# Test Selenium with Firefox
print("\n3. Testing Selenium with Firefox:")
try:
    options = Options()
    options.add_argument("--headless")
    # Try different binary locations
    for binary in ["/usr/bin/firefox", "/usr/bin/firefox-esr", "/usr/lib/firefox-esr/firefox-esr"]:
        if os.path.exists(binary):
            print(f"Trying binary: {binary}")
            options.binary_location = binary
            break
    
    service = Service('/usr/local/bin/geckodriver')
    
    driver = webdriver.Firefox(service=service, options=options)
    print("Success! Firefox WebDriver created.")
    driver.quit()
    print("Driver closed successfully.")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
