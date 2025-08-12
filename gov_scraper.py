import requests, re, concurrent.futures
from bs4 import BeautifulSoup
import pandas as pd
from gov_scraper_person import Person


# Parse the organisations from the response
def parseOrganisations(response, element, elementClass):
    soup = BeautifulSoup(response.content, "html.parser")
    return soup.find_all(element, class_=elementClass)

# Fetch the page and print the status
def getPage(baseURL):
    response = requests.get(baseURL)
    if response.status_code == 200:
        return response
    else:
        print(f"Failed to fetch the page. Status code: {response.status_code}")
        exit()

# Find the people associated with an organisation
def parsePeople(organisation, personElement):
    person_obj = Person()

    person_obj.addOrganisation(organisation)

    position_element = personElement.find("a")
    person_position = position_element.text.strip()
    person_obj.addPosition(person_position)

    name_element = position_element.find_next("a")
    person_name = name_element.text.strip()
    person_obj.addName(person_name)

    phone_element = personElement.find('a', attrs={"data-original-title": "Phone Number"})
    if phone_element:
        person_phone = phone_element.get_text(strip=True)
        person_obj.addPhone(person_phone)
                    
    email_element = personElement.find('a', attrs={"data-original-title": "Email"})
    if email_element:
        person_email = email_element.get_text(strip=True)
        person_obj.addEmail(person_email)

    return person_obj

# Finds the text within an element
def findText(element, text):
    return element.find(lambda tag: text in tag.get_text())

# Parses the key people and prints their details
def parseKeyPeople(element, organisation):
    people = element.find_all("li", class_="list-group-item")
    for person in people:
        return parsePeople(organisation, person)

# Appends a person object to the records list
def appendPerson(person_obj):
    records.append({
        "Name": person_obj.name,
        "Organisation": person_obj.organisation,
        "Department": person_obj.department,
        "Position": person_obj.position,
        "Phone": person_obj.phone,
        "Email": person_obj.email,
    })

# Recursively find subsectors and parse their key people
def findSubsectors(element, sector_name, organisation):
    subsectors = element.find_all("li")
    for subsector in subsectors:
        if subsector.find("ul"):
            inner_subsectors = subsector.find("ul")
            findSubsectors(inner_subsectors, sector_name)
        else:
            a_tag = subsector.find("a")
            if a_tag:
                subsector_href = a_tag["href"]
                subsector_page = getPage(baseURL + subsector_href)
                subsector_results = parseOrganisations(subsector_page, "section", ["views-element-container", "block-directory-custom"])
                for subsector_result in subsector_results:
                    if findText(subsector_result, "Key People"):
                        person_obj = parseKeyPeople(subsector_result, organisation)
                        person_obj.department = subsector.text.strip()
                        appendPerson(person_obj)

def scrapeBoards(element, organisation, text, department=None):
    if findText(element, text):
        role = element.find_all('a', href=re.compile(r"^/portfolios/"))
        people = element.find_all('a', href=re.compile(r"^/people/"))
        for i, person in enumerate(people):
            person_obj = Person()
            person_obj.addOrganisation(organisation)
            person_obj.addDepartment(department)
            person_obj.addPosition(role[i].text.strip())
            person_obj.addName(person.text.strip())
            appendPerson(person_obj)

# Use DFS to scrape all people from the root page and its section and board pages.
def scrape_organisation(result):
    phone = None
    a_tag = result.find("a")
    if a_tag:
        organisation = result.text.strip()
        href = a_tag["href"]  # Extract the href attribute
        organisation_page = getPage(baseURL + href)
        organisation_results = parseOrganisations(organisation_page, "section", ["views-element-container", "block-directory-custom"])

        for organisation_result in organisation_results:
            # ===========
            # Checks for immediate people listed within the organisation
            # ===========
            if findText(organisation_result, "Key People"):
                person_obj = parseKeyPeople(organisation_result, organisation)
                appendPerson(person_obj)

            # ===========
            # Checks for sub-sectors within the organisation (assume the section hierarchy has only two levels)
            # ===========
            if findText(organisation_result, "Sections"):
                subsector_name = ""
                findSubsectors(organisation_result, subsector_name, organisation)

            # ===========
            # Checks for executive appointments
            # ===========
            scrapeBoards(organisation_result, organisation, "Current single executive appointments", department=None)

            # ===========
            # Checks for linked boards
            # ===========
            if findText(organisation_result, "Government appointed boards"):
                boards = organisation_result.find_all("li")
                for board in boards:
                    board_name = board.text.strip()
                    a_tag = board.find("a")
                    if a_tag:
                        board_href = a_tag["href"]
                        board_page = getPage(baseURL + board_href)
                        board_results = parseOrganisations(board_page, "section", ["views-element-container", "block-directory-custom"])
                        for board_result in board_results:
                            scrapeBoards(board_result, organisation, "Current board appointments", department=board_name)

# Main loop to iterate through each organisation
records = []

baseURL = 'https://www.directory.gov.au'
page = getPage(baseURL + '/commonwealth-entities-and-companies')
results = parseOrganisations(page, "td", "views-field views-field-title")

if __name__ == '__main__':
    # Use a thread pool to concurrently scrape
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        executor.map(scrape_organisation, results)

df = pd.DataFrame(records)
excel_filename = "government_profiles.xlsx"
df.to_excel(excel_filename, index=False)
print(f"\n✅ Done. Exported {len(records)} profiles to {excel_filename}")