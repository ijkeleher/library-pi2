#!/usr/bin/env python
'''
@author Inci Keleher

This file contains the endpoints for website pages
current it is a single page app however this may change in future

Code modified from Tutorial code
'''

import json
import requests
import flask_login
from flask import Blueprint, render_template

site = Blueprint("site", __name__)

# Client webpage.
@site.route("/")
@flask_login.login_required
def index():
    """
    This is the root directory single page "library dashboard"
    """
    # Use REST API.
    response = requests.get("http://127.0.0.1:5000/book")
    data = json.loads(response.text)

    users_response = requests.get("http://127.0.0.1:5000/user")
    users_data = json.loads(users_response.text)

    loan_response = requests.get("http://127.0.0.1:5000/bookborrowed")
    loan_data = json.loads(loan_response.text)

    return render_template(
        "index.html",
        books=data,
        users=users_data,
        loans=loan_data)
