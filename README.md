# Welcome to Our Library System Application

## Activate the virtualenv (OS X & Linux)
$ source myproject/bin/activate
## Activate flask app for hot reload (dev environment)
$ export FLASK_ENV=development 
$ export FLASK_APP=app.py
$ flask run --host=0.0.0.0
## set flask ,env
$ echo "FLASK_ENV=development \
FLASK_APP=app.py" >> .flaskenv
