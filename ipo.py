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
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


results = []

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
                (By.XPATH, "//span[contains(text(),'Apply for Issue')]")
            )
        )
        apply_for_issue.click()

        company_list = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located(
                (By.CSS_SELECTOR, ".company-list .row.align-items-center")
            )
        )

        print(f"📈 Found {len(company_list)} companies in the list.")

        for company in company_list:
            # Get the share-of-type element
            share_of_type = company.find_element(
                By.CSS_SELECTOR, ".share-of-type"
            ).text.strip()

            # Check if the share-of-type is either FPO or IPO
            if share_of_type in ["FPO", "IPO"]:
                print(f"Found company with share type: {share_of_type}")

                # Click the Apply button for this company
                apply_button = company.find_element(By.CSS_SELECTOR, ".btn-issue")
                apply_button.click()
                print("✅ Clicked Apply button for the company.")

                select_bank = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.ID, "selectBank"))
                )
                select_bank.click()
                second_bank_option = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable(
                        (By.XPATH, "//select[@id='selectBank']/option[2]")
                    )
                )
                second_bank_option.click()

                # Wait for the accountNumber dropdown and select the second option
                account_number = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.ID, "accountNumber"))
                )
                account_number.click()
                second_account_option = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable(
                        (By.XPATH, "//select[@id='accountNumber']/option[2]")
                    )
                )
                second_account_option.click()

                # Wait for the appliedKitta input field and fill it with 10
                applied_kitta = WebDriverWait(driver, 10).until(
                    EC.visibility_of_element_located((By.ID, "appliedKitta"))
                )
                applied_kitta.send_keys("10")

                # Wait for the crnNumber input field and fill it with the CRN from the account
                crn_number = WebDriverWait(driver, 10).until(
                    EC.visibility_of_element_located((By.ID, "crnNumber"))
                )
                crn_number.send_keys(account["crn"])

                # Check the disclaimer checkbox
                disclaimer_checkbox = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.ID, "disclaimer"))
                )
                disclaimer_checkbox.click()

                # Click the Proceed button
                proceed_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable(
                        (By.XPATH, "//button[span[text()='Proceed']]")
                    )
                )
                proceed_button.click()

                transaction_pin = WebDriverWait(driver, 10).until(
                    EC.visibility_of_element_located((By.ID, "transactionPIN"))
                )
                transaction_pin.send_keys(account["mpin"])

                # Click the Apply button
                apply_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable(
                        (By.XPATH, "//button[span[text()='Apply ']]")
                    )
                )
                apply_button.click()
                try:
                    # Wait for the toast element to appear
                    toast_element = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located(
                            (
                                By.XPATH,
                                "//div[contains(@class, 'toast') and contains(@class, 'ng-trigger')]",
                            )
                        )
                    )
                    # Get the class attribute of the toast
                    toast_class = toast_element.get_attribute("class")
                    print(f"Toast class: {toast_class}")

                    # Locate the toast message inside the toast element
                    toast_message_element = WebDriverWait(toast_element, 10).until(
                        EC.presence_of_element_located((By.CLASS_NAME, "toast-message"))
                    )
                    # Get the class attribute of the toast
                    toast_class = toast_element.get_attribute("class")
                    print(f"Toast class: {toast_class}")

                    # Get the text of the toast message
                    toast_message = toast_message_element.text
                    print(f"Toast message: {toast_message}")

                    # Check if the toast indicates success or failure
                    if "toast-error" in toast_class:
                        print(f"❌ Application failed: {toast_message}")
                    elif "toast-success" in toast_class:
                        print(f"✅ Application succeeded: {toast_message}")
                    else:
                        print(f"⚠️ Unexpected toast type: {toast_message}")
                except Exception as e:
                    print(f"❌ Failed to retrieve toast message: {e}")

                # Add a small delay to avoid overwhelming the server
                time.sleep(2)
                if "toast-error" in toast_class:
                    results.append(
                        f"Name: {account['name']}\nStatus: ❌ Application failed: {toast_message}"
                    )
                elif "toast-success" in toast_class:
                    results.append(
                        f"Name: {account['name']}\nStatus: ✅ Application succeeded: {toast_message}"
                    )
                else:
                    results.append(
                        f"Name: {account['name']}\nStatus: ⚠️ Unexpected toast type: {toast_message}"
                    )

                print("✅ Login successful!")

    except Exception as e:
        results.append(f"Name: {account['name']}\nStatus: ❌ Login failed: {e}")

    finally:
        driver.quit()


def send_email(results):
    sender_email = os.environ.get("SENDER_EMAIL")
    sender_password = os.environ.get("SENDER_PASSWORD")
    recipient_email = os.environ.get("RECIPIENT_EMAIL")
    subject = "IPO Application Results"
    body = "\n".join(results)
    msg = MIMEMultipart()
    msg["From"] = sender_email

    msg["To"] = recipient_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, recipient_email, msg.as_string())
        print("✅ Email sent successfully!")
    except Exception as e:
        print(f"❌ Failed to send email: {e}")


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

send_email(results)
