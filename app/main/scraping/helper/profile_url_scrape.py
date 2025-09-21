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



def scrape_linkedin_people_search(names, email, password, cookies_file="linkedin_cookies.json"):
    """
    Enhanced LinkedIn scraper with cookie handling:
    - Saves cookies after first login and reuses them for subsequent sessions
    - Only logs in once per session, then uses cookies for remaining requests
    - Handles multiple names by looping through them
    - Saves separate HTML files for each name's search outcome
    - Uses proxy rotation every 3 names
    """
    batch_size = 5  # Change proxy every 3 names
    first_batch = True  # Track if this is the first batch (needs login)
    
    # Check if cookies exist and load them
    if os.path.exists(cookies_file) and not first_batch:
        print("Found existing cookies file. Will try to use saved session.")
    
    for i in range(0, len(names), batch_size):
        batch_names = names[i:i + batch_size]
        
        driver = uc.Chrome(headless=True)
        try:
            # For the first batch, check if we need to login
            if first_batch:
                # Load existing cookies if available
                if load_cookies(driver, cookies_file):
                    print("Cookies loaded, checking session validity...")
                else:
                    print("No cookies found. Performing login...")
                    from linkedin_scraper import actions
                    actions.login(driver, email, password)
                    print("Login submitted, waiting for confirmation...")
                    save_cookies(driver, cookies_file)
                    print("Login successful! Cookies saved for future use.")
                
        
                first_batch = False  # Set to False after first batch
            
            
            # Scrape each name in the batch
            for j, name in enumerate(batch_names):
                print(f"  Scraping {j+1}/{len(batch_names)}: {name}")
                
                try:
                    # URL-encode the name (replace spaces with %20)
                    encoded_name = name.replace(' ', '%20')
                    url = f"https://www.linkedin.com/search/results/people/?keywords={encoded_name}"
                    
                    # Navigate to the search page
                    print(f"    Navigating to: {url}")
                    driver.get(url)
                    
                    # Wait for page to load and search results to appear
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.TAG_NAME, "body"))
                    )
                    time.sleep(random.uniform(2, 4))  # Random wait to mimic human behavior
                    
                    # Check if we got redirected to login (session expired)
                    if "login" in driver.current_url.lower():
                        print(f"    Session expired for {name}. Re-logging in...")
                        from linkedin_scraper import actions
                        actions.login(driver, email, password)
                        save_cookies(driver, cookies_file)
                        # Retry the URL
                        driver.get(url)
                        time.sleep(3)
                    
                
                    # get all <a> 
                    links = driver.find_elements(By.TAG_NAME, "a")

                    
                    found = False  

                    for link in links:
                        href = link.get_attribute("href")  
                        if href and "linkedin.com/in/" in href:  
                            print("found url:",href)  
                            found = True  
                            break  

                    if not found:
                        print("could not find any linkedin profile link on the search results page.")
                    
                    # Random delay between searches to avoid detection
                    if j < len(batch_names) - 1:  # Don't wait after last name in batch
                        wait_time = random.uniform(1, 3)
                        print(f"    Waiting {wait_time:.1f}s before next search...")
                        time.sleep(wait_time)
                
                except Exception as scrape_error:
                    print(f"    ✗ Error scraping {name}: {scrape_error}")
                    
        
        except Exception as batch_error:
            print(f"Batch error: {batch_error}")
        
        finally:
            # Clean up driver after batch
            print("Closing browser...")
            driver.quit()
            
            # Delay between batches
            if i + batch_size < len(names):
                batch_delay = random.uniform(3, 7)
                print(f"Waiting {batch_delay:.1f}s before next batch...")
                time.sleep(batch_delay)
    
    print("Scraping completed!")