import requests, re, concurrent.futures
from bs4 import BeautifulSoup
from typing import Optional, List

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


def parse_organisations(response: requests.Response, element: str, element_class: str):
    """Parse the organisations from a response."""
    soup = BeautifulSoup(response.content, "html.parser")
    return soup.find_all(element, class_=element_class)


def parse_people(person_element, organisation: str, location: Optional[str]) -> Person:
    """Extract person details from a 'Key People' entry."""
    person = Person()
    person.addOrganisation(organisation)
    person.addLocation(location)

    # Position and name
    position_element = person_element.find("a")
    if position_element:
        person.addPosition(position_element.text.strip())

        name_element = position_element.find_next("a")
        if name_element:
            person.addName(name_element.text.strip())

    # Contact info
    phone_element = person_element.find('a', attrs={"data-bs-original-title": "Phone Number"})
    if phone_element:
        person.addPhone(phone_element.get_text(strip=True))
    
    email_element = person_element.find('a', attrs={"data-bs-original-title": "Email"})
    if email_element:
        person.addEmail(email_element.get_text(strip=True))

    return person


def find_text(element, text: str):
    """Find element containing specific text."""
    return element.find(lambda tag: text in tag.get_text())


def parse_location(element) -> Optional[str]:
    """Parse location for organisation."""
    location = element.find("div", class_="building-location")
    if location:
        return location.find("a").get_text(strip=True)
    return None


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


def person_to_model(person: Person) -> GovPeople:
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
        business_phone=person.phone,
        mobile_phone=None,   # Not scraped
        email=person.email,
        sector=person.department,
    )


def scrape_organisation(result):
    """Scrape an organisation and return list of GovPeople."""
    org_people = []

    a_tag = result.find("a")
    if not a_tag:
        return []

    organisation = result.text.strip()
    href = a_tag["href"]

    org_page = get_page(BASE_URL + href)
    if not org_page:
        return []

    org_results = parse_organisations(org_page, "section", ["views-element-container", "block-directory-custom"])
    if not org_results:
        return []

    location = parse_location(org_results[1]) if len(org_results) > 1 else None

    for org_result in org_results:
        # Key People
        if find_text(org_result, "Key People"):
            people_objs = parse_key_people(org_result, organisation, location)
            org_people.extend([person_to_model(p) for p in people_objs])

        # Executive appointments
        board_people = scrape_boards(org_result, "Current single executive appointments", organisation, location)
        org_people.extend([person_to_model(p) for p in board_people])

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

                board_results = parse_organisations(board_page, "section", ["views-element-container", "block-directory-custom"])
                for board_result in board_results:
                    board_people = scrape_boards(board_result, "Current board appointments", organisation, location, department=board_name)
                    org_people.extend([person_to_model(p) for p in board_people])

    return org_people

# TODO: add exception handling
def update_gov_database():
    """Main entrypoint: scrape and update DB."""
    page = get_page(BASE_URL + '/commonwealth-entities-and-companies')
    if not page:
        raise Exception(f"Failed to load main government page, URL:${BASE_URL}/commonwealth-entities-and-companies")

    results = parse_organisations(page, "td", "views-field views-field-title")

    all_people = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        for org_people in executor.map(scrape_organisation, results):
            all_people.extend(org_people)   # org_people is a list of dicts

    # Commit in batches using your commit_batch
    batch_size = 1000
    for i in range(0, len(all_people), batch_size):
        batch = all_people[i:i + batch_size]
        commit_batch(batch)  

    print(f"✅ Inserted/updated {len(all_people)} records into gov_people")

