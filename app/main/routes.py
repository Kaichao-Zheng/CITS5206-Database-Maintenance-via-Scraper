import os
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash
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

@bp.route("/settings", methods=["GET", "POST"])
@login_required
def settings():
    form = SettingsForm()
    error = None

    # Load the initial password from .env
    load_dotenv()
    env_admin_pwd = os.getenv("ADMIN_PASSWORD", "")

    if request.method == "POST":
        old_pwd = form.old_password.data
        new_pwd = form.new_password.data
        repeat_pwd = form.repeat_new_password.data

    # New password rule validation (backend fallback)
        import re
        def valid_pwd(pwd):
            return (
                len(pwd) >= 8 and
                re.search(r'[A-Za-z]', pwd) and
                re.search(r'\d', pwd) and
                re.search(r'[!@#$%^&*()_+\-=\[\]{};\'":\\|,.<>\/?]', pwd)
            )

    # Determine whether the current user has set a password in the database
        user = User.query.filter_by(id=current_user.id).first()
        if user.password_hash is None or user.password_hash == "" or user.password_hash == generate_password_hash(env_admin_pwd):
            # First time using .env password
            if not old_pwd or old_pwd != env_admin_pwd:
                error = "The old password is incorrect."
        else:
            # Database password
            if not user.check_password(old_pwd):
                error = "The old password is incorrect."

        if not error and not valid_pwd(new_pwd):
            error = "The new password must be at least 8 characters long and contain letters, numbers, and special characters."
        if not error and new_pwd != repeat_pwd:
            error = "The new password and confirmation password do not match."

        if error:
            flash(error, "error")
            return render_template("settings.html", nav="settings", form=form)

    # Change password
        user.set_password(new_pwd)
        db.session.commit()
        flash("Password changed successfully. Please log in again.", "success")
        logout_user()
        return redirect(url_for("main.index"))

    return render_template("settings.html", nav="settings", form=form)
@bp.route("/logs")
@login_required
def logs():
    return render_template("logs.html", nav="logs", )

