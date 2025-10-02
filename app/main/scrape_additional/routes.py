from flask import flash, redirect, url_for, request, jsonify
from flask_login import login_required
from app.main.scrape_additional import sca
from .helper.gov_scraper import update_gov_database
from .helper.gov_database import search_database

@sca.route('/update_local_db', methods=['GET'])
@login_required
def update_local_db():
    try:
        update_gov_database()
        flash("Database updated successfully", "success")
    except Exception as e:
        flash(f"Error updating database: {e}", "error")
    return redirect(request.referrer or url_for("main.workspace"))

@sca.route('/search_local_db', methods=['POST'])
@login_required
def search_local_db():
    try:
        """
        This endpoint expects a JSON payload in the following format:
        [
            ["John", "Doe"],
            ["Jane", "Smith"]
        ]


        Request example:
            fetch("/search_local_db", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify([
                    ["John", "Doe"],
                    ["Jane", "Smith"]
                ])
            })
            .then(res => res.json())
            .then(data => console.log(data));
        """

        data = request.get_json()

        # Here data is already a list of [fname, lname]
        results = []
        for fname, lname in data:
            res = search_database(fname, lname)
            results.append(res)

        return jsonify({"results": results}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500