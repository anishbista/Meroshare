from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import Select

import time


accounts = {
    "dp": "174",
    "username": "02950001",
    "password": "02950001",
}

CHROMEDRIVER_PATH = "/usr/bin/chromedriver"


def login(account):
    options = webdriver.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    service = Service(CHROMEDRIVER_PATH)
    driver = webdriver.Chrome(service=service, options=options)

    try:
        driver.get("https://meroshare.cdsc.com.np/#/login")
        time.sleep(2)

        dp_dropdown = driver.find_element(By.ID, "selectBranch")
        select = Select(dp_dropdown)
        select.select_by_value(account["dp"])
        time.sleep(1)

        # Enter Username and Password
        driver.find_element(By.ID, "username").send_keys(account["username"])
        driver.find_element(By.ID, "password").send_keys(account["password"])

        # Click Login Button
        driver.find_element(By.XPATH, "//button[contains(text(),'Login')]").click()
        time.sleep(3)  # Wait for login

        print("✅ Login successful!")

    except Exception as e:
        print(f"❌ Login failed: {e}")

    finally:
        driver.quit()


# Run login function
login(accounts)
