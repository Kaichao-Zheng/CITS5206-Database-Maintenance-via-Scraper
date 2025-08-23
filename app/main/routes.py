from app.main import bp
from flask import Flask, render_template,flash, redirect,url_for
import sqlalchemy as sa
from app import db
from app.models import User
from app.main.forms import LoginForm
from flask_login import current_user, login_user

@bp.route("/", methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
def index():
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.scalar(
            sa.select(User).where(User.username == form.username.data))
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for(''))
        return redirect('/workspace')
    return render_template(
        "index.html", form=form
    )
