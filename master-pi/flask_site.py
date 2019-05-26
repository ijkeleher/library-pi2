'''
@author Inci Keleher

This file contains the endpoints for website pages
current it is a single page app however this may change in future

Code modified from Tutorial code
'''

from flask import Flask, Blueprint, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import os
import requests
import json
import flask_login


site = Blueprint("site", __name__)

# Client webpage.
@site.route("/")
@flask_login.login_required
def index():
    # Use REST API.
    response = requests.get("http://127.0.0.1:5000/book")
    data = json.loads(response.text)

    users_response = requests.get("http://127.0.0.1:5000/user")
    users_data = json.loads(users_response.text)

    loan_response = requests.get("http://127.0.0.1:5000/bookborrowed")
    loan_data = json.loads(loan_response.text)

    return render_template("index.html", books=data, users=users_data, loans=loan_data)
