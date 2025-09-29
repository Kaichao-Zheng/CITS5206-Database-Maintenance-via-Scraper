from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def get_linkedin_location(driver, profile_url, timeout=15):
    driver.get(profile_url)
    profile_container = WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((By.CLASS_NAME, "mt2"))
    )
    location_element = profile_container.find_element(
        By.CSS_SELECTOR, "span.text-body-small.inline.t-black--light.break-words"
    )
    return location_element.text.strip()