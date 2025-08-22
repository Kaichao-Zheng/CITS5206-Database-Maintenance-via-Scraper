from app.main import bp
from flask import Flask, render_template


@bp.route("/")
@bp.route('/index')
def index():
    user = {'username': 'Miguel'}
    return render_template(
        
        "index.html",  user=user
    )
