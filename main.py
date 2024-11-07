import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException

# Set Chrome options to keep the browser open
chrome_options = webdriver.ChromeOptions()
chrome_options.add_experimental_option("detach", True)

# Initialize WebDriver
driver = webdriver.Chrome(options=chrome_options)
driver.get("https://orteil.dashnet.org/experiments/cookie/")

# Locate the cookie element
cookie = driver.find_element(By.ID, "cookie")

# Function to extract the cost from a power-up element
def get_cost(button):
    try:
        cost_text = button.find_element(By.TAG_NAME, "b").text.split("-")[1].strip()
        return int(cost_text.replace(",", ""))  # Convert to integer (remove commas)
    except Exception as e:
        print(f"Error getting cost: {e}")
        return float("inf")  # If cost cannot be fetched, return infinity

# Function to safely fetch a button element with WebDriverWait
def get_button(button_id):
    try:
        return WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.ID, button_id))
        )
    except TimeoutException:
        print(f"Button {button_id} not found.")
        return None

# Function to click the most expensive affordable power-up
def buy_most_expensive():
    try:
        money = int(driver.find_element(By.ID, "money").text.replace(",", ""))
    except ValueError:
        money = 0  # Handle case where money is not available

    # Collect all power-up buttons with their IDs
    upgrades = {
        "buyCursor": "Cursor",
        "buyGrandma": "Grandma",
        "buyFactory": "Factory",
        "buyMine": "Mine",
        "buyShipment": "Shipment",
        "buyAlchemy lab": "Alchemy lab",
        "buyPortal": "Portal",
        "buyTime machine": "Time machine",
    }

    # Find the most expensive affordable upgrade
    most_expensive = None
    highest_cost = 0

    for button_id, name in upgrades.items():
        button = get_button(button_id)
        if button:
            try:
                cost = get_cost(button)
                if cost <= money and cost > highest_cost:
                    most_expensive = button
                    highest_cost = cost
            except StaleElementReferenceException:
                print(f"{name} became stale. Skipping.")

    # If there is an affordable upgrade, buy it
    if most_expensive:
        try:
            most_expensive.click()
            print(f"Bought {most_expensive.get_attribute('id')} for {highest_cost} cookies.")
        except (StaleElementReferenceException, Exception) as e:
            print(f"Error clicking {most_expensive.get_attribute('id')}: {e}")

# Main loop: Continuously click the cookie and buy upgrades every 5 seconds
last_check_time = time.time()

while True:
    cookie.click()  # Click the cookie

    # Check for upgrades every 5 seconds
    if time.time() - last_check_time >= 5:
        buy_most_expensive()
        last_check_time = time.time()

    time.sleep(0.01)  # Avoid high CPU usage with a small sleep
