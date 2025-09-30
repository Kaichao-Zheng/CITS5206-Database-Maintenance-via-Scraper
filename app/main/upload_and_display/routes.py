from app.main.upload_and_display import ud
from flask import render_template,flash, redirect,url_for,request, jsonify,send_file,current_app
import sqlalchemy as sa
from app import db
from app.models import User,People, Log, LogDetail
from app.main.forms import UploadForm
from flask_login import current_user, login_user,logout_user,login_required
import pandas as pd
from charset_normalizer import detect
from requests.exceptions import RequestException
from io import TextIOWrapper, BytesIO
from flask_mail import Message, Mail
from threading import Thread
from app.main.scrape.helper.scrape_information import scrape_and_update_people
import io
import csv
from app.main.scrape_additional.helper.gov_database import get_last_update

field_mapping = {
            "FirstName": "first_name",
            "LastName": "last_name",
            "Salutation": "salutation",
            "Organization": "organization",
            "Role": "role",
            "Gender": "gender",
            "City (if outside AUS)": "city",
            "State AUS only": "state",
            "Country": "country",
            "Business Phone": "business_phone",
            "Mobile Phone": "mobile_phone",
            "EmailAddress": "email",
            "Sector": "sector",
            "Linkedin": "linkedin"
        }

@ud.route("/excel_display", methods=["GET"])
@login_required
def excel_display():

    last_update = get_last_update()

    return render_template("/excel_display.html", nav="workspace", last_update=last_update)

@ud.route("/upload", methods=["POST"])
@login_required
def upload(): 
    if "file" not in request.files:
        flash("Please select a file", "danger")
        return redirect(url_for("main.workspace"))
    
    file = request.files.get("file")

    # Read the file content and remove NULL bytes
    file_content = file.read().replace(b'\x00', b'')
    
    # Detect file encoding, default to utf-8-sig to handle BOM
    detected = detect(file_content)
    encoding = detected.get('encoding', 'utf-8-sig') or 'utf-8-sig'

    text_file = TextIOWrapper(BytesIO(file_content), encoding=encoding)
    try:
        df = pd.read_csv(text_file, engine="c")
        df.columns = df.columns.str.strip()
        df = df[[col for col in df.columns if col in field_mapping]].rename(columns=field_mapping)
        
        # Validate required fields
        required_fields = ["first_name", "last_name"]
        for field in required_fields:
            if field not in df.columns:
                flash(f"Missing required column: {field}", "danger")
                return redirect(url_for("main.workspace"))
            
        # Add missing columns
        for expected_col in field_mapping.values():
            if expected_col not in df.columns:
                df[expected_col] = "" 

        people = df.to_dict(orient="records")

        # Clear and insert
        db.session.query(People).delete()
        for person in people:
            db.session.execute(
                sa.insert(People).values(**person)
            )
        db.session.commit()

        flash(f"Uploaded {len(people)} people successfully!", "success")
        return redirect(url_for("upload_and_display.excel_display")) 

    except Exception as e:
        db.session.rollback()
        flash(f"Upload failed: {str(e)}", "danger")
        return redirect(url_for("main.workspace"))
    
@ud.route("/data", methods=["GET"])
@login_required
def get_data():
    people = db.session.query(People).all()
    data = [p.as_dict() for p in people]  
    return jsonify(data)

@ud.route("/update",methods=["POST"])
@login_required
def update():
    payload = request.get_json()
    source = payload.get("source")
    data = payload.get("data")
    log = Log(status="in_progress")
    db.session.add(log)
    db.session.commit()
    if not source or not data:
        return jsonify({"status": "error", "error": "Missing source or data"}), 400
    user_email = current_user.email
    app = current_app._get_current_object()
    thread = Thread(target=process_update_task, args=(app,user_email, source, log.id))
    thread.start()
    return jsonify({"status": "success", "log_id": log.id}), 202


@ud.route("/export", methods=["GET"])
@login_required
def export_data():
    people = db.session.query(People).all()
    df = pd.DataFrame([p.as_dict() for p in people])
    output = BytesIO()
    df.to_excel(output, index=False)
    output.seek(0)
    return send_file(output,
                     download_name="people.xlsx",
                     as_attachment=True)


def process_update_task(app,user_email, source, log_id):
    # Your processing / database update logic
    # Example: save CSV temporarily
    print(f"Starting update for user: {user_email}")
    with app.app_context():

        try:
            if source == "linkedin":
                scrape_and_update_people(log_id)
            elif source == "gw":
                # #TODO: handle Government Website update
                # process_gw(data)
                pass
            else:
                return jsonify({"status": "error", "error": "Invalid source"}), 400

            print("Update successful")
        except Exception as e:
            db.session.rollback()
            print("Update failed:", str(e))
            return jsonify({"error": str(e)}), 500
        
        # Step 4: Fetch all People (or limit to updated ones if you prefer)
        all_people = db.session.query(People).all()

        # Step 5: Write CSV to memory (no temp file needed)
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow([col.name for col in People.__table__.columns])  # header row
        for p in all_people:
            writer.writerow([getattr(p, col.name) for col in People.__table__.columns])

        csv_data = output.getvalue()
        output.close()

        with open("updated.csv", "w", newline='', encoding='utf-8') as f:
            f.write(csv_data)
        

        # TODO: Send email to user
        # msg = Message(
        #     subject="Your updated CSV is ready",
        #     recipients=[user_email],
        #     body=f"Your {source} data has been updated. See attached CSV.",
        # )
        # with app.open_resource(csv_file) as fp:
        #     msg.attach(f"updated_{source}.csv", "text/csv", fp.read())
        # mail.send(msg)


@ud.route("/updating/<int:log_id>")
@login_required
def updating(log_id):
    return render_template("updating.html", log_id=log_id, nav="workspace")


@ud.route("/update_progress/<int:log_id>")
@login_required
def update_progress(log_id):
    log = db.session.get(Log, log_id)
    if not log:
        return jsonify({"error": "Log not found"}), 404
    people = db.session.query(People).all()
    details = db.session.query(LogDetail).filter_by(log_id=log_id).all()
    total = len(people)
    completed = sum(1 for d in details if d.status in ("success", "error"))
    
    return jsonify({
        "status": log.result or "In progress",
        "total": total,
        "completed": completed,
        "details": [
            {"record_name": d.record_name, "status": d.status, "source": d.source}
            for d in details
        ]
    })

@ud.route("/update_complete")
@login_required
def update_complete():
    return render_template("update-complete.html", nav="workspace")