from flask import Blueprint

ud = Blueprint("upload_and_display", __name__)

from app.main.upload_and_display import routes