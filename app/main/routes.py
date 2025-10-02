import os
from dotenv import load_dotenv
from app.main import bp
from flask import Flask, render_template,flash, redirect,url_for,request, jsonify
import sqlalchemy as sa
from app import db
from app.main.forms import UploadForm
from flask_login import login_required
from app.models import Log, LogDetail

bad_lines = []
def handle_bad_line(line):
    # line is a list of strings (the row values), CSV is not uniform.
    bad_lines.append(line)
    return None 

@bp.route("/workspace", methods=["GET"])
@login_required
def workspace():
    form = UploadForm()

    return render_template("/workspace.html", nav="workspace", form=form)

@bp.route("/update") # TODO: pass the log id and log records
@login_required
def update():

    return render_template("update.html", nav="workspace")

@bp.route("/logs")
@login_required
def logs():
    logs = Log.query.order_by(Log.created_at.desc()).all()
    return render_template("logs.html", logs=logs, nav="logs")

@bp.route("/logs/<int:log_id>/details")
def log_details(log_id):
    details = LogDetail.query.filter_by(log_id=log_id).all()
    data = [
        {
            "record_name": d.record_name,
            "status": d.status,
            "source": d.source,
            "detail": d.detail
        }
        for d in details
    ]
    return jsonify(data)