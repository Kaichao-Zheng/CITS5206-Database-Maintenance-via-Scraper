import os
from dotenv import load_dotenv
from app.main import bp
from flask import Flask, render_template,flash, redirect,url_for,request, jsonify
import sqlalchemy as sa
from app import db
from app.main.forms import UploadForm
from flask_login import login_required
from .scrape_additional.helper.gov_database import get_last_update


bad_lines = []
def handle_bad_line(line):
    # line is a list of strings (the row values), CSV is not uniform.
    bad_lines.append(line)
    return None 

@bp.route("/workspace", methods=["GET"])
@login_required
def workspace():
    form = UploadForm()

    last_update = get_last_update()

    return render_template("/workspace.html", nav="workspace", form=form, last_update=last_update)

@bp.route("/update") # TODO: pass the log id and log records
@login_required
def update():
    return render_template("update.html", nav="workspace",)

@bp.route("/logs")
@login_required
def logs():
    return render_template("logs.html", nav="logs", )

