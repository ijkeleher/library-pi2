#!/usr/bin/env python3
import os
from datetime import datetime
from flask import Flask, render_template, request
from flask_bootstrap import Bootstrap

app = Flask(__name__)
bootstrap = Bootstrap(app)

def getData():
    time = datetime.now().strftime("%H:%M:%S")
    motd = "Welcome to the library"
    return time, motd

 # main route 
@app.route("/")

def index():    
    time, motd = getData()
    templateData = {
                    'time': time,
                    'motd': motd
                   }
    return render_template('index.html', **templateData)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
