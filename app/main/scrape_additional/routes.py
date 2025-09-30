from flask import flash, redirect, url_for, request
from flask_login import login_required
from app.main.scrape_additional import sca
from .helper.gov_scraper import update_gov_database

@sca.route('/update_local_db', methods=['GET'])
@login_required
def update_local_db():
    try:
        update_gov_database()
        flash("Database updated successfully", "success")
    except Exception as e:
        flash(f"Error updating database: {e}", "error")
    return redirect(request.referrer or url_for("main.workspace"))