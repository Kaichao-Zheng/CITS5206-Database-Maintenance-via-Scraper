from flask import Blueprint

sc = Blueprint("scrape", __name__)

from app.main.scrape import routes