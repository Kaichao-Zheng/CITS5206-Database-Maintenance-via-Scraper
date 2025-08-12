import time
import random
import pandas as pd
import os
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from linkedin_scraper import Person, actions

# ====================
# Helpers
# ====================

def human_delay(a=1.5, b=4.0):
    time.sleep(random.uniform(a, b)) # Random delay to mimic human behavior

def random_scroll(driver):
    scroll_script = f"window.scrollBy(0, {random.randint(-300, 300)});"
    driver.execute_script(scroll_script)
    human_delay(1, 2)

# ====================
# Setup WebDriver
# ====================

# Match, install, and start a ChromeDriver
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)
#driver = webdriver.Chrome()

# ====================
# Automated user authentication (assume does NOT require MFA or Captcha)
# ====================

load_dotenv()
email = os.getenv("LINKEDIN_EMAIL")
password = os.getenv("LINKEDIN_PASSWORD")
actions.login(driver, email, password)
# human_delay(3, 6)

# ====================
# Name list
# ====================

name_list = [
    # "Andre Iguodala",
    "Adam D'Angelo",
    "Satya Nadella"
    # example names, you can add more
]

# ====================
# Data collection
# ====================

records = []

for name in name_list:
    print(f"\nSearching for: {name}")
    try:
        # Search a person in LinkedIn
        search_url = f"https://www.linkedin.com/search/results/people/?keywords={name.replace(' ', '%20')}"
        driver.get("https://www.linkedin.com")
        driver.get(search_url)
#         human_delay(3, 6)
        # Mimic human scrolls
        for _ in range(random.randint(3, 6)):
            random_scroll(driver)

        # Locate name elements in DOM tree to get profile links
        container = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "search-results-container"))
        )

        ul = container.find_element(By.TAG_NAME, "ul")
        li_list = ul.find_elements(By.TAG_NAME, "li")

        if li_list:
            first_li = li_list[0]           # Assume the target profile always ranks first
            a_tag = first_li.find_element(By.TAG_NAME, "a")
            href = a_tag.get_attribute("href").split('?mini')[0]

            if href and "/in/" in href:
                print("Opening profile:", href)
                profile_url = href
#                 human_delay(4, 7)

                # scrape profile page
                person = Person(profile_url,driver=driver,scrape=True,close_on_complete=False)
#                human_delay(3, 6)
#                person.scrape(close_on_complete=False)
                name = person.name or ""                                            # mapped to 'FirstName', 'LastName'
                location = person.location or ""                                    # mapped to 'City', 'State', 'Country'
                company = person.company or ""                                      # mapped to 'Institution'
                contacts = person.contacts or ""                                    # mapped to 'Phone', 'Email'
                
                # scrape recent experiences
                position_title = ""
                if person.experiences:
                    position_title = person.experiences[0].position_title or ""     # mapped to 'Role'
                    # institution_name = person.experiences[0].institution_name or "" # mapped to 'Institution'

                

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
            else:
                print("No valid profile link found.")
        else:
            print("No <li> elements found.")
    except Exception as e:
        print("Error during search/profile:", e)

    # delay
    human_delay(2,4)

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