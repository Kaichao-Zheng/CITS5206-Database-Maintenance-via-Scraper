from flask import Blueprint

sca = Blueprint("scrape_additional", __name__)

from app.main.scrape_additional import routes