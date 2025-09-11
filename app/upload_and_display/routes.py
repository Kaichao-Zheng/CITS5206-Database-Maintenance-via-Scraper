from app.main import bp
from flask import Flask, render_template,flash, redirect,url_for,request, jsonify
import sqlalchemy as sa
from app import db
from app.models import User,People, Log, LogDetail
from app.main.forms import LoginForm,UploadForm
from flask_login import current_user, login_user,logout_user,login_required
import pandas as pd
from charset_normalizer import detect
from requests.exceptions import RequestException
from io import TextIOWrapper, BytesIO

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

@bp.route("/upload", methods=["POST"])
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
        db.session.execute(sa.insert(Log).values()) # TODO: implement logging bad lines
        db.session.commit()
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
        return redirect(url_for("main.workspace")) # TODO: redirect to update

    except Exception as e:
        db.session.rollback()
        flash(f"Upload failed: {str(e)}", "danger")
        return redirect(url_for("main.workspace"))
