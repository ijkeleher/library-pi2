from flask import Flask, Blueprint, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import os, requests, json

site = Blueprint("site", __name__)

# Client webpage.
@site.route("/")
def index():
    # Use REST API.
    response = requests.get("http://127.0.0.1:5000/book")
    data = json.loads(response.text)

    users_response = requests.get("http://127.0.0.1:5000/user")
    users_data = json.loads(users_response.text)

    loan_response = requests.get("http://127.0.0.1:5000/bookborrowed")
    loan_data = json.loads(loan_response.text)


    return render_template("index.html", books = data, users = users_data, loans = loan_data)
