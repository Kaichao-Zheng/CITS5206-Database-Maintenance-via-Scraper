import undetected_chromedriver as uc
import time
import random
import json
import os
from selenium.webdriver.common.by import By
from .profile_url_scrape import load_cookies, save_cookies
from linkedin_scraper import Person
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def close_alert_if_present(driver):
    try:
        alert = driver.switch_to.alert
        alert.accept()
        print("Alert closed!")
    except Exception:
        pass  # No alert to close

def human_delay(min_delay, max_delay):
    delay_time = random.uniform(min_delay, max_delay)
    print(f"Waiting for {delay_time:.2f} seconds...")
    time.sleep(delay_time)

def scrape_profiles(profile_map, EMAIL, PASSWORD):
    driver = uc.Chrome(headless=True)
    cookies_file = "my_linkedin_cookies.json"
    results_dict = {}

    if load_cookies(driver, cookies_file):
        print("Cookies loaded, checking session validity...")

    try:
        for name, profile_url in profile_map.items():
            print(f"Scraping profile for {name}: {profile_url}")
            try:
                person = Person(profile_url, driver=driver, scrape=False)
                close_alert_if_present(driver)
                human_delay(1, 3)

                # Wait for page load
                try:
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "body"))
                    )
                    print(f"Profile page loaded for {name}")
                except Exception as e:
                    print(f"❌ Failed to load profile page for {name}: {e}")
                    continue

                # Scrape name and location
                try:
                    person.get_name_and_location()
                    print(f"Name and location scraped for {name}")
                except Exception as e:
                    print(f"⚠️ Failed to scrape name/location for {name}: {e}")
                    # Continue with empty values
                    person.name = ""
                    person.location = ""

                # Scrape experiences
                try:
                    person.get_experiences()
                    print(f"Experiences scraped for {name}")
                except Exception as e:
                    print(f"⚠️ Failed to scrape experiences for {name}: {e}")
                    person.company = ""
                    person.job_title = ""

                # Store results with fallback empty values
                results_dict[name] = {
                    "company": person.company or "",
                    "position": person.job_title or "",
                    "location": person.location or ""
                }
                print(f"✅ Scraped {name}: {results_dict[name]}")

            except Exception as e:
                print(f"❌ Error processing profile for {name}: {e}")
                continue  # Skip to next profile

    finally:
        driver.quit()

    return results_dict

