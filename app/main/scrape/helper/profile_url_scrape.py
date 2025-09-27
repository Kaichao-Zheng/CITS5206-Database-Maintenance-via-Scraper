import time
import json
import os
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import random
import undetected_chromedriver as uc
import re
from urllib.parse import urlparse, urlunparse
from linkedin_scraper import actions


def save_cookies(driver, filename="linkedin_cookies.json"):
    """Save cookies to file after successful login"""
    cookies = driver.get_cookies()
    with open(filename, 'w') as f:
        json.dump(cookies, f)
    print(f"Cookies saved to {filename}")

def load_cookies(driver, filename="linkedin_cookies.json"):
    """Load cookies from file and add to driver"""
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            cookies = json.load(f)
        
        # Navigate to LinkedIn main page first to set domain
        driver.get("https://www.linkedin.com")
        
        # Add each cookie
        for cookie in cookies:
            try:
                # Remove 'SameSite' attribute as it's not supported in older Selenium versions
                if 'sameSite' in cookie:
                    del cookie['sameSite']
                driver.add_cookie(cookie)
            except Exception as e:
                print(f"Error adding cookie {cookie.get('name', 'unknown')}: {e}")
        
        # Refresh the page to apply cookies
        driver.refresh()
        time.sleep(2)
        print(f"Cookies loaded from {filename}")
        return True
    else:
        print(f"Cookie file {filename} not found. Need to login first.")
        return False

def init_driver(headless=False):
    """Safe Chrome init"""
    options = uc.ChromeOptions()
    if headless:
        options.add_argument("--headless=new")
    options.add_argument("--disable-blink-features=AutomationControlled")
    driver = uc.Chrome(options=options)
    return driver

def scrape_linkedin_people_search(names, cookies_file="linkedin_cookies.json"):
    """
    Enhanced LinkedIn scraper with cookie handling:
    - Saves cookies after first login and reuses them for subsequent sessions
    - Only logs in once per session, then uses cookies for remaining requests
    - Handles multiple names by looping through them
    - Saves separate HTML files for each name's search outcome
    - Uses proxy rotation every 3 names
    """
    batch_size = 20
    first_batch = True
    results = {}

    email = os.getenv("LINKEDIN_EMAIL")
    password = os.getenv("LINKEDIN_PASSWORD")

    for i in range(0, len(names), batch_size):
        batch_names = names[i:i + batch_size]

        driver = init_driver(headless=False)
        try:
            driver.get("https://www.linkedin.com/")

            # Load cookies if available
            if load_cookies(driver, cookies_file):
                driver.refresh()
                print("🔑 Cookies loaded.")
            else:
                print("No cookies found, logging in...")
                actions.login(driver, email, password)
                save_cookies(driver, cookies_file)
                print("✅ Logged in and cookies saved.")

            first_batch = False

            for j, name in enumerate(batch_names):
                print(f"\n👤 Scraping {j+1}/{len(batch_names)}: {name}")
                encoded_name = name.replace(" ", "%20")
                search_url = f"https://www.linkedin.com/search/results/people/?keywords={encoded_name}"

                try:
                    driver.get(search_url)
                    time.sleep(random.uniform(5, 10))

                    WebDriverWait(driver, 1).until(
                        EC.presence_of_element_located((By.TAG_NAME, "body"))
                    )

                    # Check if redirected to login/authwall
                    if "login" in driver.current_url.lower() or "authwall" in driver.current_url.lower():
                        print("⚠️ Redirected to login/authwall, re-logging in...")
                        actions.login(driver, email, password)
                        save_cookies(driver, cookies_file)
                        driver.get(search_url)
                        time.sleep(5)

                    # Extract first LinkedIn profile link
                    links = driver.find_elements(By.TAG_NAME, "a")
                    found = False
                    for link in links:
                        href = link.get_attribute("href")
                        if href and "linkedin.com/in/" in href:
                            clean_url = urlunparse(urlparse(href)._replace(query=''))
                            print(f"✅ Found URL for {name}: {clean_url}")
                            results[name] = clean_url
                            found = True
                            break
                    if not found:
                        print(f"⚠️ No LinkedIn profile link found for {name}")

                    # Random delay between searches
                    if j < len(batch_names) - 1:
                        time.sleep(random.uniform(1, 3))

                except Exception as scrape_error:
                    print(f"❌ Error scraping {name}: {scrape_error}")

        except Exception as batch_error:
            print(f"❌ Batch error: {batch_error}")

        finally:
            print("Closing browser...")
            driver.quit()
            if i + batch_size < len(names):
                time.sleep(random.uniform(3, 7))
            print("Batch completed.\n")

    return results