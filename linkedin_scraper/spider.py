import time
import random
import pandas as pd
import os
# from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from linkedin_scraper import Person, actions
from selenium.common.exceptions import TimeoutException
from dotenv import load_dotenv
from get_location import get_linkedin_location
from google_scraper import scrape_google_emails_highlight, scrape_google_emails_fulltext

# ====================
# Helpers
# ====================


def human_delay(a=1.5, b=4.0):
    time.sleep(random.uniform(a, b)) # Random delay to mimic human behavior

def random_scroll(driver):
    scroll_script = f"window.scrollBy(0, {random.randint(-300, 300)});"
    driver.execute_script(scroll_script)
    human_delay(1, 2)
    
def close_alert_if_present(driver):
    try:
        WebDriverWait(driver, 2).until(EC.alert_is_present())
        alert = driver.switch_to.alert
        alert.dismiss()  # 或 alert.accept()
        print("Alert dismissed")
    except TimeoutException:
        pass

# ====================
# Setup WebDriver
# ====================
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/114.0.0.0 Safari/537.36"
)

# create the Chromeoption
options = webdriver.ChromeOptions()
options.add_argument(f"user-agent={USER_AGENT}")
options.add_argument("--headless")  # Run in headless mode
# option: mimic genuine user
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--start-maximized")

driver = webdriver.Chrome()
load_dotenv()
email = os.getenv("LINKEDIN_EMAIL")
password = os.getenv("LINKEDIN_PASSWORD")
actions.login(driver, email, password)


# ====================
# Name list
# ====================

name_list = [
    "Andre Iguodala",
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
        # enter search url
        search_url = f"https://www.linkedin.com/search/results/people/?keywords={name.replace(' ', '%20')}"
        driver.get(search_url)
        close_alert_if_present(driver)
#         human_delay(3, 6)
        # Mimic human scrolls
        for _ in range(random.randint(3, 6)):
            random_scroll(driver)

        # position information that we want 
        container = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "search-results-container"))
            )
        
        first_result_div = container.find_element(By.CSS_SELECTOR, "div[data-view-name='search-entity-result-universal-template']")

        a_tag = first_result_div.find_element(By.TAG_NAME, "a")
        href = a_tag.get_attribute("href").split('?mini')[0]

        if href and "/in/" in href:
            print("Opening profile:", href)
            profile_url = href
#                 human_delay(4, 7)
            driver.get(profile_url)

            location = get_linkedin_location(driver, profile_url)
            print("Location:", location)

            # scrape information 
            person = Person(profile_url,driver=driver,scrape=False)
            close_alert_if_present(driver)
            human_delay(1, 3)
            person.get_experiences()
            close_alert_if_present(driver)
            company = person.company or ""
            
            # get the positiontitle
            position_title = ""
            if person.experiences:
                position_title = person.experiences[0].position_title or ""
            
            print("Name:", name)
            print("Company:", company)
            print("Position:", position_title)
            emails = scrape_google_emails_highlight(name, company, driver)
            
            print("email:", emails)

            # record to record list
            records.append({
                "Name": name,
                "Company": company,
                "Position": position_title,
                "Location": location,
                "Emails": emails
            })
        else:
            print("No valid profile link found.")
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
driver.quit()