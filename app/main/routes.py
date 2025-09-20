from app.main import bp
from flask import Flask, render_template,flash, redirect,url_for,request, jsonify
import sqlalchemy as sa
from app import db
from app.models import User,People, Log, LogDetail
from app.main.forms import LoginForm,UploadForm
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
    return render_template("settings.html", nav="settings")

@bp.route("/logs")
@login_required
def logs():
    return render_template("logs.html", nav="logs", )

