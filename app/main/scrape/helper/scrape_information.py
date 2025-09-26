import undetected_chromedriver as uc
import time
import random
import json
import os
from selenium.webdriver.common.by import By
from .profile_url_scrape import load_cookies, save_cookies
from linkedin_scraper import Person
from selenium.webdriver.support.ui import WebDriverWait,EC

def close_alert_if_present(driver):
    try:
       
        alert = driver.switch_to.alert
        alert.accept()
        print("Alert closed!")
    except Exception as e:
        pass  # No alert to close

def human_delay(min_delay, max_delay):
    delay_time = random.uniform(min_delay, max_delay)
    print(f"Waiting for {delay_time:.2f} seconds...")
    time.sleep(delay_time)

def scrape_profiles(profile_map, EMAIL, PASSWORD):
    driver = uc.Chrome(headless=False)
    cookies_file = "my_linkedin_session.json"
    results_dict = {}

    if load_cookies(driver, cookies_file):
        print("Cookies loaded, checking session validity...")

    try:
        for name, profile_url in profile_map.items():
            print(f"Scraping profile for {name}: {profile_url}")
            person = Person(profile_url, driver=driver, scrape=False)

            close_alert_if_present(driver)
            human_delay(1, 3)

            try:
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "body"))
                )
                print(f"Profile page loaded for {name}")
            except Exception as e:
                print(f"❌ Failed to load profile page for {name}: {e}")
                continue

            person.get_name_and_location()
            person.get_experiences()

            company = person.company or ""
            position_title = person.job_title or ""
            location = person.location or ""

            results_dict[name] = {
                "company": company,
                "position": position_title,
                "location": location
            }

            print(f"✅ Scraped {name}: {results_dict[name]}")
    finally:
        driver.quit()

    return results_dict

