from flask import Blueprint

sc = Blueprint("scraping", __name__)

from app.main.scrape import routes