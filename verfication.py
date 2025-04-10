import os
import threading
import json
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

ACCOUNTS_FILE = "accounts.json"
if not os.path.exists(ACCOUNTS_FILE):
    raise FileNotFoundError(f"❌ {ACCOUNTS_FILE} not found!")

with open(ACCOUNTS_FILE, "r") as file:
    accounts = json.load(file)
GECKODRIVER_PATH = "/usr/bin/chromedriver"  # Update this path if necessary


def login(account):
    options = webdriver.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    # options.add_argument("--headless")

    service = Service(GECKODRIVER_PATH)
    driver = webdriver.Chrome(service=service, options=options)

    try:
        driver.get("https://meroshare.cdsc.com.np/#/login")

        # Wait for the DP dropdown to be clickable
        dp_dropdown = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "selectBranch"))
        )
        dp_dropdown.click()  # Open the dropdown

        # Wait for the desired option to be present and clickable
        desired_option = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, f"//li[contains(text(), '{account['dp']}')]")
            )
        )
        desired_option.click()
        driver.maximize_window()

        # Wait for the username field to be visible and enter the username
        username_field = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.ID, "username"))
        )
        username_field.send_keys(account["username"])

        # Wait for the password field to be visible and enter the password
        password_field = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.ID, "password"))
        )
        password_field.send_keys(account["password"])

        # Wait for the login button to be clickable and click it
        login_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Login')]"))
        )
        login_button.click()

        # Wait for navigation to complete
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "sidebar-nav"))
        )

        my_asba_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//span[contains(text(),'My ASBA')]"))
        )
        my_asba_button.click()
        print("📥 Navigated to My ASBA.")

        apply_for_issue = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, "//span[contains(text(),'Application Report')]")
            )
        )
        apply_for_issue.click()

        # Wait for company list to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".company-list"))
        )

        # Get fresh reference to company list elements
        company_list = driver.find_elements(
            By.CSS_SELECTOR, ".company-list .row.align-items-center"
        )

        print(f"📈 Found {len(company_list)} companies in the list.")

        for index in range(len(company_list)):
            # Re-find the company list each iteration to avoid staleness
            company_list = driver.find_elements(
                By.CSS_SELECTOR, ".company-list .row.align-items-center"
            )
            company = company_list[index]

            try:
                share_of_type = company.find_element(
                    By.CSS_SELECTOR, ".share-of-type"
                ).text.strip()
                print(f"Found company with share type: {share_of_type}")

                # Click the Report button for this company
                apply_button = company.find_element(By.CSS_SELECTOR, ".btn-issue")
                apply_button.click()
                print("✅ Clicked Report button for the company.")

                # Wait for report details to load
                try:

                    company_name_element = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located(
                            (By.CSS_SELECTOR, "span[tooltip='Company Name']")
                        )
                    )
                    company_name = company_name_element.text.strip()

                    application_date = (
                        WebDriverWait(driver, 10)
                        .until(
                            EC.presence_of_element_located(
                                (
                                    By.XPATH,
                                    "//label[text()='Application submitted date']/../../div[2]//label",
                                )
                            )
                        )
                        .text.strip()
                    )

                    status = (
                        WebDriverWait(driver, 10)
                        .until(
                            EC.presence_of_element_located(
                                (
                                    By.XPATH,
                                    "//label[text()='Status']/../../div[2]//label",
                                )
                            )
                        )
                        .text.strip()
                    )

                    log_filename = f"{account['username']}_log.txt"
                    current_date = time.strftime("%Y-%m-%d")

                    with open(log_filename, "a") as log_file:
                        log_file.write(
                            f"✅ {current_date}: {company_name} | Application Date: {application_date} | Status: {status}\n"
                        )

                    print(f"✅ Logged details for {company_name}")

                except Exception as e:
                    print(f"❌ Failed to load company details: {e}")
                    continue

                # Go back to the company list
                driver.back()
                # Wait for company list to reload
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".company-list"))
                )

            except Exception as e:
                print(f"❌ Error processing company {index}: {e}")
                continue

        print("✅ Completed processing all companies.")

    except Exception as e:
        print(f"❌ Login failed: {e}")

    finally:
        driver.quit()


# Create and start threads for each account
threads = []
for i, account in enumerate(accounts):
    thread = threading.Thread(target=login, args=(account,))
    threads.append(thread)
    thread.start()

    if i < len(accounts) - 1:  # Add delay between launches
        time.sleep(5)

# Wait for all threads to complete
for thread in threads:
    thread.join()
