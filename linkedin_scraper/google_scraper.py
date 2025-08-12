import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def scrape_google_emails_highlight(name, company,driver=None):
    created_driver = False
    if driver is None:
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                                    "Chrome/119 Safari/537.36")
        driver = webdriver.Chrome(options=chrome_options)
        created_driver = True
    
    
    query = f"{name} {company} email info"
    email_pattern = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-z]{2,}')
    
    try:
        driver.get("https://www.google.com")
        
        # Accept consent if appears
        try:
            consent_btn = WebDriverWait(driver, 3).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Accept')]"))
            )
            consent_btn.click()
        except:
            pass
        
        search_box = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.NAME, "q"))
        )
        search_box.send_keys(query)
        search_box.send_keys(Keys.RETURN)
        
        WebDriverWait(driver, 5).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "em"))
        )
        
        marks = driver.find_elements(By.CSS_SELECTOR, "em")
        texts = [el.text.strip() for el in marks if el.text.strip()]
        
        emails = [t for t in texts if email_pattern.fullmatch(t)]
        return emails
    finally:
        if created_driver:
            driver.quit()
        
def scrape_google_emails_fulltext(name, company):
    created_driver = False
    if driver is None:
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                                    "Chrome/119 Safari/537.36")
        driver = webdriver.Chrome(options=chrome_options)
        created_driver = True
    
    
    query = f"{name} {company} email info"
    email_pattern = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-z]{2,}')
    
    try:
        driver.get("https://www.google.com")
        
        # Accept consent if appears
        try:
            consent_btn = WebDriverWait(driver, 3).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Accept')]"))
            )
            consent_btn.click()
        except:
            pass
        
        search_box = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.NAME, "q"))
        )
        search_box.send_keys(query)
        search_box.send_keys(Keys.RETURN)
        
        WebDriverWait(driver, 5).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div#search"))
        )
        
        results = driver.find_elements(By.CSS_SELECTOR, "div#search")
        emails_found = set()
        
        for result in results:
            text = result.text
            matches = email_pattern.findall(text)
            for email in matches:
                emails_found.add(email)
        
        return list(emails_found)
    finally:
        if created_driver:
            driver.quit()
        
# if __name__ == "__main__":
#     name = "Jeff Weiner"
#     company = "Santander US"

#     emails_from_marks = scrape_google_emails_highlight(name, company)
#     # print("Emails from <mark> highlights:", emails_from_marks)

#     emails_from_fulltext = scrape_google_emails_fulltext(name, company)
#     # print("Emails from full text:", emails_from_fulltext)

#     all_emails = list(set(emails_highlight + emails_fulltext))  
#     email_record = {"email": all_emails}
#     # print(email_record)