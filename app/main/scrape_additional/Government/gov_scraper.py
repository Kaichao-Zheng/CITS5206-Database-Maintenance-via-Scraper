import requests, re, concurrent.futures
from bs4 import BeautifulSoup
from typing import Optional, List
from urllib.parse import urljoin, urlparse
import threading

from app.main.scrape_additional.Government.gov_scraper_person import Person
from app.main.scrape_additional.Government.gov_database import commit_batch
from app.models import GovPeople

BASE_URL = 'https://www.directory.gov.au'
UA = "Perth USAsia Centre/1.0 (+contact: lisa.cluett@perthusasia.edu.au)"

session = requests.Session()
session.headers.update({"User-Agent": UA})

def get_page(url: str) -> Optional[requests.Response]:
    """Fetch a webpage and return its response object."""
    try:
        response = session.get(url, timeout=15)
        response.raise_for_status()
        return response
    except requests.RequestException as e:
        print(f"Request failed: {e}")
        return None


def parse_organisation_info(soup):
    """Extract phone, email, and location from the organisation's contact section."""
    contact_info = {
        "phone": None,
        "email": None,
        "location": None
    }

    contact_container = soup.find("div", class_="view-content container")
    if not contact_container:
        return contact_info
    
    contact_info["phone"] = (
        contact_container.find("span", class_="text-phone").get_text(strip=True)
        if contact_container.find("span", class_="text-phone") 
        else None
    )

    contact_info["email"] = (
        contact_container.find("span", class_="text-email").get_text(strip=True)
        if contact_container.find("span", class_="text-email")
        else None
    )

    location_elem = contact_container.find("div", class_="building-location")
    if location_elem and location_elem.find("a"):
        contact_info["location"] = location_elem.find("a").get_text(strip=True)

    return contact_info

def parse_people(person_element, organisation: str, location: Optional[str]) -> Person:
    """Extract person details from a 'Key People' entry."""
    person = Person()
    person.addOrganisation(organisation)
    person.addLocation(location)

    # Position and name
    links = person_element.find_all("a")
    if links:
        person.addPosition(links[0].get_text(strip=True))
        if len(links) > 1:
            person.addName(links[1].get_text(strip=True))

    # Contact info
    phone_element = person_element.find('a', attrs={"data-original-title": "Phone Number"})
    if phone_element:
        person.addPhone(phone_element.get_text(strip=True))
    
    email_element = person_element.find('a', attrs={"data-original-title": "Email"})
    if email_element:
        person.addEmail(email_element.get_text(strip=True))

    return person


def find_text(element, text: str):
    """Find element containing specific text."""
    return element.find(lambda tag: text in tag.get_text())


def parse_key_people(element, organisation: str, location: Optional[str]) -> List[Person]:
    """Parse all people under 'Key People'."""
    people = []
    entries = element.find_all("li", class_="list-group-item")
    for entry in entries:
        people.append(parse_people(entry, organisation, location))
    return people


def scrape_boards(element, text, organisation, location, department=None) -> List[Person]:
    """Scrape board appointments."""
    people_objs = []
    if find_text(element, text):
        roles = element.find_all('a', href=re.compile(r"^/portfolios/"))
        people = element.find_all('a', href=re.compile(r"^/people/"))
        for i, person in enumerate(people):
            person_obj = Person()
            person_obj.addOrganisation(organisation)
            person_obj.addDepartment(department)
            if i < len(roles):
                person_obj.addPosition(roles[i].text.strip())
            person_obj.addName(person.text.strip())
            person_obj.addLocation(location)
            people_objs.append(person_obj)
    return people_objs


def person_to_model(person: Person, fallback_info) -> GovPeople:
    """Map Person object to GovPeople model instance."""
    return GovPeople(
        salutation=person.salutation,
        first_name=person.fname,
        last_name=person.lname,
        organization=person.organisation,
        role=person.position,
        gender=person.gender,
        city=person.city,
        state=person.state,
        country=person.country,
        business_phone=person.phone if person.phone else fallback_info["phone"],
        mobile_phone=None,   # Not scraped
        email=person.email if person.email else fallback_info["email"],
        sector=person.department,
    )

def normalise_url(url: str) -> str:
    """
    Normalize URL by:
    - Lowercasing
    - Removing trailing slashes
    - Removing fragments
    """
    parsed = urlparse(url)
    normalized = parsed._replace(fragment="") # Remove #fragment
    path = normalized.path.rstrip("/") # Remove trailing slash
    return urljoin(f"{normalized.scheme}://{normalized.netloc}", path).lower()

visited = set()
visited_lock = threading.Lock()

def scrape_sections(soup):
    """Scrape and recurse into 'Sections' links within an organisation page."""
    section_block = soup.find("section", class_="block-directory-custom-section-block")
    if not section_block:
        return []

    section_links = section_block.find_all("li", class_="list-group-item")
    if not section_links:
        return []

    all_people = []
    for link in section_links:

        a_tag = link.find("a")
        if not a_tag:
            continue
        href = a_tag["href"]
        if not href:
            continue

        section_url = BASE_URL + href

        # Skip already visited URLs
        if normalise_url(section_url) in visited:
            continue

        with visited_lock: # Ensure thread-safe access to visited set
            visited.add(normalise_url(section_url))

        section_results = scrape_organisation(link)
        all_people.extend(section_results)

    return all_people


def scrape_organisation(result):
    """Scrape an organisation and return list of GovPeople."""
    org_people = []

    a_tag = result.find("a")
    if not a_tag:
        return []

    organisation = result.text.strip()
    href = a_tag["href"]
    if not href:
        return []

    org_page = get_page(BASE_URL + href)

    with visited_lock: # Ensure thread-safe access to visited set
        visited.add(normalise_url(BASE_URL + href))

    if not org_page:
        return []

    soup = BeautifulSoup(org_page.content, "html.parser")

    fallback_info = parse_organisation_info(soup)

    org_results = soup.find_all("section", class_=["views-element-container", "block-directory-custom"])
    if not org_results:
        return []

    location = fallback_info["location"]

    for org_result in org_results:
        # Key People
        if find_text(org_result, "Key People"):
            people_objs = parse_key_people(org_result, organisation, location)
            org_people.extend([person_to_model(p, fallback_info) for p in people_objs])

        # Executive appointments
        board_people = scrape_boards(org_result, "Current single executive appointments", organisation, location)
        org_people.extend([person_to_model(p, fallback_info) for p in board_people])

        # Linked boards
        if find_text(org_result, "Government appointed boards"):
            boards = org_result.find_all("li")
            for board in boards:
                board_name = board.text.strip()
                a_tag = board.find("a")
                if not a_tag:
                    continue

                board_href = a_tag["href"]
                board_page = get_page(BASE_URL + board_href)
                if not board_page:
                    continue

                # 🔧 Manual inline parsing again
                board_soup = BeautifulSoup(board_page.content, "html.parser")
                board_results = board_soup.find_all("section", class_=["views-element-container", "block-directory-custom"])
                for board_result in board_results:
                    board_people = scrape_boards(
                        board_result,
                        "Current board appointments",
                        organisation,
                        location,
                        department=board_name
                    )
                    org_people.extend([person_to_model(p, fallback_info) for p in board_people])

    # Search through linked sections
    section_people = scrape_sections(soup)
    org_people.extend(section_people)

    return org_people


def update_gov_database():
    """Main entrypoint: scrape and update DB."""
    page = get_page(BASE_URL + '/commonwealth-entities-and-companies')
    if not page:
        raise Exception(f"Failed to load main government page, URL:{BASE_URL}/commonwealth-entities-and-companies")

    soup = BeautifulSoup(page.content, "html.parser")
    results = soup.find_all("td", class_="views-field views-field-title")

    all_people = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        for org_people in executor.map(scrape_organisation, results):
            all_people.extend(org_people)

    # Commit in batches
    batch_size = 1000
    for i in range(0, len(all_people), batch_size):
        batch = all_people[i:i + batch_size]
        commit_batch(batch)  

    print(f"✅ Inserted/updated {len(all_people)} records into gov_people")
