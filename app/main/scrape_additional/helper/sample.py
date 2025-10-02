from .gov_scraper import update_gov_database
from .gov_database import search_database

update_gov_database()

search_database("John", "Smith")
search_database("Jane", "Thomson")