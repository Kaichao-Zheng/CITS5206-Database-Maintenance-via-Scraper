from flask import jsonify
from flask_login import login_required
from app.main.scrape_additional import sca
from .helper.gov_scraper import update_gov_database

@sca.route('/update_local_db', methods=['GET'])
@login_required
def update_local_db():
    try:
        update_gov_database()
        return jsonify({"message": "Database updated successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500