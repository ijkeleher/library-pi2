# Welcome to Our Library System Application

* IoT Python application running on 2x Raspberry Pi
* Utilises facial recognition and image detection for book borrowing
* Flask API and Admin Dashboard for tracking book loan data
* Google Cloud SQL used for database
* Google Data Studio used for analytics

### Library functions API
https://documenter.getpostman.com/view/6571696/S1M3uQMp?version=latest&fbclid=IwAR381X4IIvZGb2-dSPBbFoUDg4N9bJXEI4cMnWPnPBb0YU82STHn_vHhmJ0

Use dropdown to switch between python-requests and curl format for GET/POST/PUT/DELETE requests

---
## Running dev environment in local

### Activate the virtualenv (OS X & Linux)
    $ source venv/bin/activate
    
### Deactivate the virtualenv (OS X & Linux)
    $ deactivate

### Activate flask app for hot reload (dev environment)
    $ export FLASK_ENV=development 
    $ export FLASK_APP=flask_main.py
    $ flask run
    
---
## Running dev environment as docker image

### install docker
on mac

    $ brew install docker-for-mac
    
linux

    $ apt-get install docker

### navigate to folder container docker-compose.yml
    $ cd path/to/master-pi
    
### create a .env file with the following
    FLASK_ENV=development
    FLASK_APP=flask_main.py
    SECRET_KEY=<key>
    DB_USER=root
    DB_PW=<pw>
    ADMIN_USER=jaqen
    ADMIN_PW=<pw>

### build docker container
    $ docker-compose build
    
### run the app
    $ docker-compose up
    
This command runs all containers defined in your docker-compose file. If it is needed – rebuild and remove old unused containers

    $ docker-compose up -d --build --remove-orphans
