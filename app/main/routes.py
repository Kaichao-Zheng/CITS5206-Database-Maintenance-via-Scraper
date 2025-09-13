from app.main import bp
from flask import Flask, render_template,flash, redirect,url_for,request, jsonify
import sqlalchemy as sa
from app import db
from app.models import User,People, Log, LogDetail
from app.main.forms import LoginForm,UploadForm, SettingsForm
from flask_login import current_user, login_user,logout_user,login_required
import pandas as pd
from requests.exceptions import RequestException
@bp.route("/", methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
def index():
    if current_user.is_authenticated:
        return redirect('/workspace')
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.scalar(
            sa.select(User).where(User.username == form.username.data))
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password', "error")
            return redirect(url_for('main.index'))
        login_user(user)
        return redirect('/workspace')
    return render_template(
        "index.html", form=form
    )

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))

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

bad_lines = []
def handle_bad_line(line):
    # line is a list of strings (the row values), CSV is not uniform.
    bad_lines.append(line)
    return None 

@bp.route("/workspace", methods=["GET"])
@login_required
def workspace():
    form = UploadForm()

    return render_template("/workspace.html", nav="workspace",form=form)

@bp.route("/update") # TODO: pass the log id and log records
@login_required
def update():
    return render_template("update.html", nav="workspace",)

@bp.route("/settings")
@login_required
def settings():
    form = SettingsForm()
    return render_template("settings.html", nav="settings",form=form)

@bp.route("/logs")
@login_required
def logs():
    return render_template("logs.html", nav="logs", )

@bp.route("/upload", methods=["POST"])
@login_required
def upload(): 
    if "file" not in request.files:
        flash("Please select a file", "danger")
        return redirect(url_for("main.workspace"))
    
    file = request.files.get("file")
    try:
        db.session.execute(sa.insert(Log).values()) # TODO: implement logging bad lines
        db.session.commit()
        df = pd.read_csv(file, engine="python", on_bad_lines=handle_bad_line)
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
