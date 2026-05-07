from flask import Blueprint, redirect, url_for, request, render_template

app_only = Blueprint('app_only', __name__)

@app_only.route("/join/<id>")
def join_discovery(id):
    return render_template('app_only.html')
