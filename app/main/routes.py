from app.main import bp
from flask import Flask, render_template,flash, redirect,url_for
import sqlalchemy as sa
from app import db
from app.models import User
from app.main.forms import LoginForm,UploadForm
from flask_login import current_user, login_user,logout_user,login_required

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
            flash('Invalid username or password')
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

@bp.route("/workspace", methods=["GET", "POST"])
@login_required
def workspace():
    form = UploadForm()
    if form.validate_on_submit():
        file = form.file.data
        # file.save(f"uploads/{file.filename}")
        flash("File uploaded successfully!")
        # return redirect(url_for("main.upload"))
    return render_template("/workspace/data.html", nav="workspace",active_tab="data",form=form)

@bp.route("/settings")
@login_required
def settings():
    return render_template("settings.html", nav="settings")

@bp.route("/logs")
@login_required
def logs():
    return render_template("logs.html", nav="workspace", active_tab="logs")