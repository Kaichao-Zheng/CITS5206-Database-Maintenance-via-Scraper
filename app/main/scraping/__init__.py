from flask import Blueprint

sc = Blueprint("scraping", __name__)

from app.main.scraping import routes