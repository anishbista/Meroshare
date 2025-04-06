from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
import time

accounts = {
    "dp": "174",
    "username": "02950001",
    "password": "02950001",
}


driver = webdriver.Firefox()


driver.get("https://meroshare.cdsc.com.np/")
time.sleep(2)

dp_dropdown = driver.find_element(By.ID, "selectBranch")


desired_option = driver.find_element(
    By.XPATH, f"//li[contains(text(), '{accounts['dp']}')]"
)
desired_option.click()


driver.find_element(By.ID, "username").send_keys(accounts["username"])


driver.find_element(By.ID, "password").send_keys(accounts["password"])


driver.find_element(By.XPATH, "//button[contains(text(),'Login')]").click()


time.sleep(5)
print("hello")

if "dashboard" in driver.current_url:
    print("Login successful!")
else:
    print("Login failed. Check credentials.")
