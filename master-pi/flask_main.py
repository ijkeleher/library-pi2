'''
@author Inci Keleher

This file contains the application logic for the admin website
    - Database init
    - Login function
    - Logout function

Site endpoints are located in flask_site.py
API endpoints located in flask_api.py

Code modified from Tutorial code
'''
from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import os, requests, json
from flask_api import api, db
from flask_site import site
import flask_login
from dotenv import load_dotenv

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))

#load super secret stuff
load_dotenv()
KEY = os.getenv("SECRET_KEY")
DB_USER = os.getenv("DB_USER")
DB_PW = os.getenv("DB_PW")
ADMIN_USER = os.getenv("ADMIN_USER")
ADMIN_PW = os.getenv("ADMIN_PW")

#set secret key
app.secret_key = KEY

# Update HOST and PASSWORD appropriately.
HOST = "35.189.9.24"
USER = DB_USER
PASSWORD = DB_PW
DATABASE = "rpdb"

app.config["SQLALCHEMY_DATABASE_URI"] = "mysql://{}:{}@{}/{}".format(USER, PASSWORD, HOST, DATABASE)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True

db.init_app(app)

#setup flask-login
login_manager = flask_login.LoginManager()
login_manager.init_app(app)

# Our mock database.
users = {ADMIN_USER: {'password': ADMIN_PW}}

class User(flask_login.UserMixin):
    pass

@login_manager.user_loader
def user_loader(email):
    if email not in users:
        return

    user = User()
    user.id = email
    return user


@login_manager.request_loader
def request_loader(request):
    email = request.form.get('email')
    if email not in users:
        return

    user = User()
    user.id = email

    # DO NOT ever store passwords in plaintext and always compare password
    # hashes using constant-time comparison!
    user.is_authenticated = request.form['password'] == users[email]['password']

    return user

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return '''
               <form action='login' method='POST'>
                <input type='text' name='email' id='email' placeholder='email'/>
                <input type='password' name='password' id='password' placeholder='password'/>
                <input type='submit' name='submit'/>
               </form>
               '''

    email = request.form['email']
    if request.form['password'] == users[email]['password']:
        user = User()
        user.id = email
        flask_login.login_user(user)
        return redirect(url_for('site.index'))

    return 'Bad login'

@app.route('/logout')
def logout():
    flask_login.logout_user()
    return 'Logged out'

@login_manager.unauthorized_handler
def unauthorized_handler():
    return 'Unauthorized'

app.register_blueprint(api)
app.register_blueprint(site)

if __name__ == "__main__":
    app.run(host = "0.0.0.0")
