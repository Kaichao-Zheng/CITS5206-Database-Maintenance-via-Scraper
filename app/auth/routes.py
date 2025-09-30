import os
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash
from app.auth import bp
from flask import Flask, render_template,flash, redirect,url_for,request, jsonify
import sqlalchemy as sa
from app import db
from app.models import User,People, Log, LogDetail
from app.auth.forms import LoginForm, ChangeEmailForm, ChangePasswordForm
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
            return redirect(url_for('auth.index'))
        login_user(user)
        return redirect('/workspace')
    
    return render_template(
        "index.html", form=form
    )

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.index'))


@bp.route("/change-password", methods=["GET", "POST"])
@login_required
def change_password():
    form = ChangePasswordForm()
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
        return redirect(url_for("auth.index"))

    return render_template("change-password.html", nav="settings", form=form)

@bp.route("/change-email", methods=["GET", "POST"])
@login_required
def change_email():
    form = ChangeEmailForm()
    if request.method == "POST":
        new_email = form.new_email.data
        if not new_email or "@" not in new_email:
            flash("Please enter a valid email address.", "error")
            return render_template("change-email.html", nav="settings", form=form)

        user = User.query.filter_by(id=current_user.id).first()
        user.email = new_email
        db.session.commit()
        flash("Email updated successfully.", "success")
        return redirect(url_for("auth.change_email"))

    return render_template("change-email.html", nav="settings", form=form)

@bp.route("/settings", methods=["GET"])
@login_required
def settings():
    return render_template("settings.html", nav="settings") 