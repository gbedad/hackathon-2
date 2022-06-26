from app import flask_app

from flask import redirect, render_template, url_for


@flask_app.route('/')
def index():
    return render_template('index.html')