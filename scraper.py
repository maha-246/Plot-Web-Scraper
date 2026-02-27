# Instead of text mapping, let's try XPath or CSS selectors to 
# directly target the values we want. This should be more 
# robust against layout changes and different label formats.

import time
from datetime import datetime
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# ================= GOOGLE SHEET =================

SCOPE = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

creds = ServiceAccountCredentials.from_json_keyfile_name(
    "credentials.json", SCOPE
)

client = gspread.authorize(creds)

sheet = client.open_by_key(
    "1Uh-g4fQmQntbmIpQ4IbOzWsN_B-izAUNZpv03oVO9hA"
).worksheet("Zameen_Listings_Tracker")

df = pd.DataFrame(sheet.get_all_records())

print("Rows in sheet:", len(df))


# ================= CHROME =================

options = uc.ChromeOptions()
options.add_argument("--start-maximized")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument(r"--user-data-dir=E:\ZameenChromeProfile")
options.add_argument(r"--disk-cache-dir=E:\uc_cache")

driver = uc.Chrome(
    options=options,
    version_main=144,
    use_subprocess=True
)


# ================= HELPERS =================

FIELD_MAP = {
    "Type": "Property Type",
    "Purpose": "Purpose",
    "Initial Amount": "Down Payment",
    "Monthly Installment": "Installment Amount",
    "Remaining Installments": "Number of Installments",
    "Bedroom(s)": "Bedrooms",
    "Bedrooms": "Bedrooms",
    "Bath(s)": "Bathrooms",
    "Bathrooms": "Bathrooms",
    "Added": "Added Date",
    "Location": "Location",
}

IGNORE_LABELS = [
    "months ago",
    "%",
    "Scheme"
]


def extract_price():
    candidates = driver.find_elements(By.XPATH, "//*[contains(text(),'PKR')]")
    for el in candidates:
        text = el.text.strip()
        if "PKR" in text and any(k in text for k in ["Lakh", "Crore", "Million", "Thousand"]):
            return text
    return ""


def extract_marla():
    marlas = []
    elems = driver.find_elements(By.XPATH, "//*[contains(text(),'Marla')]")
    for el in elems:
        text = el.text.strip()
        parts = text.split()
        if len(parts) == 2 and parts[1] == "Marla":
            try:
                marlas.append(float(parts[0]))
            except:
                continue
    if marlas:
        return str(min(marlas))
    return ""


def extract_contact_info():
    agent = ""
    agency = ""
    phone = ""

    try:
        # Click Call button / icon
        call_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, "//button[contains(text(),'Call')] | //span[contains(text(),'Call')]")
            )
        )
        driver.execute_script("arguments[0].click();", call_btn)
        time.sleep(2)

        # Phone number (now visible)
        phone_el = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, "//a[contains(@href,'tel')]")
            )
        )
        phone = phone_el.text.strip()

        # Parent container (important!)
        container = phone_el.find_element(By.XPATH, "./ancestor::div")

        # Agent name
        try:
            agent = container.find_element(
                By.XPATH, ".//h5 | .//strong"
            ).text.strip()
        except:
            pass

        # Agency name
        try:
            agency = container.find_element(
                By.XPATH, ".//p | .//span"
            ).text.strip()
        except:
            pass

    except:
        pass

    return agent, agency, phone


# ================= SCRAPER =================

def scrape_listing(url):
    driver.get(url)

    try:
        WebDriverWait(driver, 40).until(
            EC.presence_of_element_located(
                (By.XPATH, "//*[contains(text(),'PKR')]")
            )
        )
    except:
        print("❌ Failed to load:", url)
        return {}

    time.sleep(5)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(3)
    driver.execute_script("window.scrollTo(0, 0);")
    time.sleep(2)

    raw = {}

    rows = driver.find_elements(By.XPATH, "//span/parent::*")
    for row in rows:
        spans = row.find_elements(By.XPATH, ".//span")
        if len(spans) != 2:
            continue

        label = spans[0].text.strip()
        value = spans[1].text.strip()

        if not label or not value or value == "-":
            continue

        if any(x.lower() in label.lower() for x in IGNORE_LABELS):
            continue

        raw[label] = value

    return raw


# ================= MAIN LOOP =================

for idx, row in df.iterrows():

    url = row.get("URL")
    status = row.get("Status")

    if not url or status == "Done":
        continue

    print("\nScraping:", url)

    raw = scrape_listing(url)
    if not raw:
        sheet.update_cell(idx + 2, df.columns.get_loc("Status") + 1, "Failed")
        continue

    clean = {}

    # Normalize fields
    for label, value in raw.items():
        col = FIELD_MAP.get(label)
        if col:
            clean[col] = value

    # Price
    price = extract_price()
    if price:
        clean["Price"] = price

    # Marla size
    marla = extract_marla()
    if marla:
        clean["Marla Size"] = marla

    # Agent & agency
    agent, agency, phone = extract_contact_info()

    if agent:
        clean["Agent Name"] = agent
    if agency:
        clean["Agency Name"] = agency
    if phone:
        clean["Phone Number"] = phone

    # Meta
    clean["Scraped On"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    clean["Status"] = "Done"

    # Write to sheet
    for col, val in clean.items():
        if col in df.columns:
            sheet.update_cell(
                idx + 2,
                df.columns.get_loc(col) + 1,
                val
            )

    time.sleep(8)

print("\n✅ All listings processed")
input("Press ENTER to close Chrome")
driver.quit()
