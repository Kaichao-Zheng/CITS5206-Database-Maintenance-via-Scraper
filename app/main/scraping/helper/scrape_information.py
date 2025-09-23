import undetected_chromedriver as uc
import time
import random
import json
import os
from selenium.webdriver.common.by import By
from .profile_url_scrape import load_cookies, save_cookies
from linkedin_scraper import Person

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

def scrape_profiles(profile_urls):
    
    driver = uc.Chrome(headless=False)
    
    # 加载 cookies
    cookies_file = "linkedin_cookies.json"  # Define the name of cookies file
    if not load_cookies(driver, cookies_file):
        print("No valid cookies found, please login manually.")
        driver.quit()
        return
    result_list = []
    
    try:
        for profile_url in profile_urls:
            print(f"Scraping profile: {profile_url}")
            
           
            person = Person(profile_url, driver=driver, scrape=False)
            
            
            close_alert_if_present(driver)
            
           
            human_delay(1, 3)
            
            
            person.get_experiences()
            
            
            close_alert_if_present(driver)
            
            
            company = person.company or ""
            position_title = ""
            if person.experiences:
                position_title = person.experiences[0].position_title or ""
            
            print("Company:", company)
            print("Position:", position_title)
            print("-" * 40)

            result_list.append({"company": company, "position": position_title})
            
            
    finally:
        
        driver.quit()