import undetected_chromedriver as uc
import time
import random
import json
import os
from selenium.webdriver.common.by import By
from .profile_url_scrape import load_cookies, save_cookies, scrape_linkedin_people_search
from linkedin_scraper import Person
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from app import db
from app.models import People,LogDetail,Log
from app.main.scrape import sc
import sqlalchemy as sa
from linkedin_scraper import actions
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from dotenv import load_dotenv

LINKEDIN_EMAIL = os.getenv("LINKEDIN_EMAIL")
LINKEDIN_PASSWORD = os.getenv("LINKEDIN_PASSWORD")

def close_alert_if_present(driver):
    try:
       
        alert = driver.switch_to.alert
        alert.accept()
        print("Alert closed!")
    except Exception as e:
        pass  # No alert to close

def save_cookies(driver, path):
    with open(path, "w") as f:
        json.dump(driver.get_cookies(), f)


def load_cookies(driver, path):
    if not os.path.exists(path):
        return False
    with open(path, "r") as f:
        cookies = json.load(f)
        for cookie in cookies:
            driver.add_cookie(cookie)
    return True

def human_delay(min_delay, max_delay):
    delay_time = random.uniform(min_delay, max_delay)
    print(f"Waiting for {delay_time:.2f} seconds...")
    time.sleep(delay_time)

def ensure_logged_in(driver, cookies_file="my_linkedin_session.json"):
    """Make sure LinkedIn session is alive."""
    driver.get("https://www.linkedin.com/feed/")
    human_delay(3, 5)

    if "login" in driver.current_url or "authwall" in driver.current_url:
        print("⚠️ Not logged in. Logging in...")
        actions.login(driver, LINKEDIN_EMAIL, LINKEDIN_PASSWORD)
        human_delay(5, 8)
        save_cookies(driver, cookies_file)
        print("✅ Logged in and cookies saved.")
    else:
        print("✅ Already logged in with cookies.")


def scrape_profiles(driver, profile_map, cookies_file="linkedin_cookies.json"):
    results_dict = {}

    # Load cookies if available
    driver.get("https://www.linkedin.com/")
    if load_cookies(driver, cookies_file):
        driver.refresh()
        print("🔑 Cookies loaded.")
    ensure_logged_in(driver, cookies_file)

    for name, profile_url in profile_map.items():
        print(f"\n👤 Scraping {name}: {profile_url}")
        driver.get(profile_url)
        # person = Person(profile_url, driver=driver, scrape=False)
        close_alert_if_present(driver)
        human_delay(4, 7)

        if "authwall" in driver.current_url or "login" in driver.current_url:
            print("⚠️ Hit authwall, retrying login...")
            ensure_logged_in(driver, cookies_file)
            driver.get(profile_url)
            human_delay(4, 6)

        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "body"))
            )
        except Exception:
            print(f"❌ Could not load profile page for {name}")
            continue
        # TODO: get company. now it seems doesn't work
        try:
            company = driver.find_element(By.CSS_SELECTOR, "span.pv-entity__secondary-title").text.strip()
        except:
            company = ""

        try:
            position_title = driver.find_element(By.CSS_SELECTOR, "h2.mt1").text.strip()
        except:
            position_title = ""
        try:
            location = driver.find_element(By.CSS_SELECTOR, ".text-body-small.inline.t-black--light.break-words").text.strip()
        except:
            location = ""

        try:
            headline = driver.find_element(By.CSS_SELECTOR, ".text-body-medium").text.strip()
        except:
            headline = ""

        

        results_dict[name] = {
            "company": company,
            "position": headline,
            "location": location,
            "url": profile_url
        }
        print(f"✅ Scraped {name}: {results_dict[name]}")
        human_delay(2, 5)

    return results_dict # structured as {name: {info_dict}}



def scrape_and_update_people(log_id, number=10):
    people_records = db.session.query(People).limit(number).all()
    log = db.session.query(Log).filter_by(id=log_id).first()
    if not people_records:
        log.result = "No People records found"
        log.status = "error"
        db.session.commit()
        return {"error": "No People records found"}

    names_to_scrape = [
        f"{p.first_name} {p.last_name} {p.organization or ''}".strip()
        for p in people_records 
        if not p.linkedin
    ]

    if names_to_scrape:
        cookies_file = "my_linkedin_cookies.json"
        scraped_urls = scrape_linkedin_people_search(names_to_scrape, cookies_file)
        for name, url in scraped_urls.items():
            parts = name.strip().split()
            first_name = parts[0]
            last_name = " ".join(parts[1:-1]) if len(parts) > 2 else (parts[1] if len(parts) > 1 else "")
            person = db.session.query(People).filter(
                sa.func.lower(People.first_name) == first_name.lower(),
                sa.func.lower(People.last_name) == last_name.lower()
            ).first()
            if person:
                person.linkedin = url

    # ✅ Create driver once here
    driver = uc.Chrome(headless=False)

    try:
        profile_map = {
            f"{p.first_name} {p.last_name}".strip(): p.linkedin
            for p in people_records if p.linkedin
        }
        scraped_info = scrape_profiles(driver, profile_map, cookies_file)

        n = 0
        for name, info in scraped_info.items():
            fn, *ln = name.strip().split()
            first_name, last_name = fn, " ".join(ln)
            person = db.session.query(People).filter(
                sa.func.lower(People.first_name) == first_name.lower(),
                sa.func.lower(People.last_name) == last_name.lower()
            ).first()
            if person:
                location = info.get("location", "")
                parts = [p.strip() for p in location.split(",")]
                
                city = parts[0] if len(parts) > 0 else ""
                state = parts[1] if len(parts) > 1 else ""
                country = parts[2] if len(parts) > 2 else ""

                person.organization = info.get("company", "")
                person.role = info.get("position", "")
                person.city = city
                person.state = state
                person.country = country
                n += 1
                log_detail = LogDetail(
                    log_id=log_id,
                    record_name=name,
                    status="success",
                    source=info.get("url", ""),
                    detail=json.dumps(info)
                )
                db.session.add(log_detail)
                db.session.commit()
            else:
                log_detail = LogDetail(
                    log_id=log_id,
                    record_name=name,
                    status="error",
                    source=info.get("url", ""),
                    detail="Person not found in database"
                )
                db.session.add(log_detail)
                db.session.commit()
    except Exception as e:
        print(f"Error during scraping and updating: {e}")
        db.session.rollback()
        log.status = "error"
        log.result = str(e)
        db.session.commit()
    finally:
        driver.quit()
        log.status = "completed"
        log.result = f"Successfully updated: {n} records, failed: {len(people_records) - n} records."
        db.session.commit()
        
    return {"message": "Scraping + update successful"}
