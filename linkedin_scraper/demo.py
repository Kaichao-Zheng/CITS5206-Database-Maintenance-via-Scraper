import pandas as pd
import os
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from linkedin_scraper import Person, actions

''' This demo script is based on the previous LinkedIn-scraper version'''

# ====================
# Setup WebDriver
# ====================

# Match, install, and start a ChromeDriver
service = Service(ChromeDriverManager().install())

options = Options()
options.add_argument("--log-level=3")
driver = webdriver.Chrome(service=service, options=options)

# ====================
# Automated user authentication (assume does NOT require MFA or Captcha)
# ====================

load_dotenv()

# ====================
# Password login
# ====================
'''
email = os.getenv("LINKEDIN_EMAIL")
password = os.getenv("LINKEDIN_PASSWORD")
actions.login(driver, email, password)
'''

# ====================
# Cookie login
# ====================
cookie = os.getenv("LI_AT_COOKIE")
cookie_err_msg = "LI_AT_COOKIE is not set. Please add it to the .env file."
assert cookie, cookie_err_msg
driver.get("https://www.linkedin.com")

driver.add_cookie({
    'name': 'li_at',
    'value': cookie,
    'domain': '.www.linkedin.com',
    'path': '/',
    'secure': True,
})

# ====================
# Name list
# ====================

name_list = [
    "Adam D'Angelo",
    "Satya Nadella"
]

url_list = [
    "https://www.linkedin.com/in/andre-iguodala-65b48ab5",
    "https://www.linkedin.com/in/satyanadella/"
]

# ====================
# Data collection
# ====================

records = []

for i, url in enumerate(url_list):
    print(f"\nSearching for: {name_list[i]}")
    
    # Search a person in LinkedIn
    profile_url = url
    driver.get(profile_url)

    # scrape profile page
    person = Person(profile_url,driver=driver,scrape=True,close_on_complete=False)
    name = person.name or ""                                            # mapped to 'FirstName', 'LastName'
    location = person.location or ""                                    # mapped to 'City', 'State', 'Country'
    company = person.company or ""                                      # mapped to 'Institution'
    contacts = person.contacts or ""                                    # mapped to 'Phone', 'Email'
    
    # scrape recent experiences
    position_title = ""
    if person.experiences:
        position_title = person.experiences[0].position_title or ""     # mapped to 'Role'

    print("Name:", name)
    print("Location:", location)
    print("Company:", company)
    print("Position:", position_title)
    print("Contacts:", contacts)        # Often empty

    # record to record list
    records.append({
        "Name": name,
        "Location:": location,
        "Company": company,
        "Position": position_title,
        "Contacts:": contacts
    })

# ====================
# Export to Excel
# ====================

df = pd.DataFrame(records)
excel_filename = "linkedin_profiles.xlsx"
df.to_excel(excel_filename, index=False)
print(f"\n✅ Done. Exported {len(records)} profiles to {excel_filename}")

# ====================
# Close
# ====================
# driver.quit()