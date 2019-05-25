#!/usr/bin/python3

import sys
import MySQLdb
import json
import hashlib, binascii, os
import getpass
import re
import socket
from shutil import copy2
from facialrecognition.recognise import Recognise

from imutils.video import VideoStream
from pyzbar import pyzbar
import datetime
import imutils
import time
import cv2
import face_recognition
import argparse
import pickle

class Menu:


    def displaymenu(self):
        print("1.Login\n2.Register new user\n3.Exit")

    def getselection(self):
        while True:
            self.displaymenu()

            try:
                selection = int(input("Enter Selection: "))

                if 6 > selection > 0:
                    return selection

            except ValueError:
                print("Error: enter valid selection")
                continue
            except EOFError:
                print("Invalid option!\n")

    def login_option(self):
        """
        Login option menu for user to select method to login
        Return:
            1 if user choose to login with email
            2 if user choose to login with username
            3 if user choose to login with facial recognition
            None if user don't want to login
        """

        print("1. Login with email\n2. Login with username\n3. Login with facial recognition\n4. Back to previous menu")

        try:
            selection = int(input("Enter login option: "))
            if selection == 1:
                return 1
            elif selection == 2:
                return 2
            elif selection == 3:
                return 3
            elif selection == 4:
                return None
        except ValueError:
            print("Invalid option!\n")
        except EOFError:
            print("Invalid option!\n")

    def get_login_detail(self, email):
        """
        Get user login information, either email or username
        Param
            if user choose to login with email
        Return 
            username or email that user need to login with
        """
        detail = ""
        if email:
            detail = str(input("Please enter your email address: "))
        else:
            detail = str(input("Please enter your username: "))
        return detail


class Userdb:

    def __init__(self, config):
        self.__conn = MySQLdb.connect(config.gethostname(), config.getdbuser(), config.getdbpass(), config.getdbname())
        self.email_addr = re.compile('^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$')

    def createuser(self):

        inputvalid = False

        chars = re.compile('^[a-zA-Z]+$')
        charsnums = re.compile('^[a-zA-Z0-9]+$')
        emailaddr = self.email_addr

        while not inputvalid:

            username = input("Enter Username: ")

            if re.fullmatch(charsnums, username) is None:
                print("Error: invalid username")
                continue

            # check if username is duplicate
            existed = self.exist_info(username, False)
            if existed:
                print("Username already taken!\n")
                continue

            passwordraw = getpass.getpass("Enter Password: ")
            confirm_password = getpass.getpass("Confirm Password: ")

            if passwordraw != confirm_password:
                print("Password doesn't match!")
                continue

            passwordhashed = self.hash_password(passwordraw)


            firstname = input("Enter First name: ")
            lastname = input("Enter Last name: ")

            if re.fullmatch(chars, firstname) is None or re.fullmatch(chars, lastname) is None:
                print("Error: invalid first or last name ")
                continue


            email = input("Enter Email: ")

            if re.fullmatch(emailaddr, email) is None:
                print("Error: invalid email ")
                continue

            # check if email is duplicate
            existed = self.exist_info(email, True)
            if existed:
                print("Email exist already!\n")
                continue

            inputvalid = True

        cursor = self.__conn.cursor()

        params = (username, passwordhashed, firstname, lastname, email)

        cursor.execute("INSERT INTO rpuser(username, password, firstname, lastname, email) VALUES (%s,%s,%s,%s,%s)", params)

        self.__conn.commit()

    def exist_info(self, info, email):
        """
        check if username already exist to prevent duplicate username
        Param:
            info: info to register for new user
            email: Trus when checking duplicate email, False for username
        Return:
            Ture if username existed already
            False otherwise
        """
        cursor = self.__conn.cursor()
        if not email:
            cursor.execute("SELECT * FROM rpuser WHERE username = %s", [info])
        else:
            cursor.execute("SELECT * FROM rpuser WHERE email = %s", [info])

        data = cursor.fetchall()
        return len(data) != 0

    def loginvalid(self):
        pass

    def hash_password(self, password):
        """Reference: https://www.vitoshacademy.com/hashing-passwords-in-python/"""
        salt = hashlib.sha256(os.urandom(60)).hexdigest().encode('ascii')
        pwdhash = hashlib.pbkdf2_hmac('sha512', password.encode('utf-8'), salt, 100000)
        pwdhash = binascii.hexlify(pwdhash)
        return (salt + pwdhash).decode('ascii')

    def verify_password(self, stored_password, provided_password):
        """Reference: https://www.vitoshacademy.com/hashing-passwords-in-python/"""
        salt = stored_password[:64]
        stored_password = stored_password[64:]
        pwdhash = hashlib.pbkdf2_hmac('sha512', provided_password.encode('utf-8'), salt.encode('ascii'), 100000)
        pwdhash = binascii.hexlify(pwdhash).decode('ascii')
        return pwdhash == stored_password

    def login(self, detail, email_login):
        """
        login at reception pi
        Param:
            detail: login detail, either username or email
            email_login: True if user choose to login with email, False if user choose to login with username
        Return:
            True if login is valid
            False otherwise
        """
        if email_login:
            if re.fullmatch(self.email_addr, detail) is None:
                print("Invalid email!")
            else:
                cursor = self.__conn.cursor()
                cursor.execute("SELECT * FROM rpuser WHERE email = %s", [detail])
                data = cursor.fetchone()
                if data is not None:
                    stored_password = data[1]

                    password = getpass.getpass("Please enter your password: ")
                    return self.verify_password(stored_password, password)
        else:
            cursor = self.__conn.cursor()
            cursor.execute("SELECT * FROM rpuser WHERE username = %s", [detail])
            data = cursor.fetchone()
            if data is not None:
                stored_password = data[1]

                password = getpass.getpass("Please enter your password: ")
                return self.verify_password(stored_password, password)


class Config:

    def __init__(self, filename):
        try:
            with open(filename) as data:
                self.__conf = json.load(data)
        except EnvironmentError:
            print("Can't open "+ filename)

    def getdbuser(self):
        return self.__conf['dbuser']

    def getdbpass(self):
        return self.__conf['dbpass']

    def getdbname(self):
        return self.__conf['dbname']

    def gethostname(self):
        return self.__conf['hostname']


class SocketSession:
    
    def __init__(self, host, port):
        self.host = host
        self.port = port
    

    def Connect(self, user):
        print("Establishing connection to remote host @ " + self.host+":"+str(self.port))
      
        self.user = user

        # Connect
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.host, self.port))

        # Start by sending user info
        self.sock.sendall(bytes(user, 'UTF-8')) 
        # Get back the main menu
        menu = self.sock.recv(4096)

        return menu

    def ConsoleSession(self):
       
        while True:
           
            # Get some user input
            inp = input("Please enter your response: ")
            
            # Shoot it off to the server
            self.sock.sendall(bytes(inp, 'UTF-8'))
           
            # Get the response
            response = str(self.sock.recv(4096), 'utf-8')
            if 'TERMINATE_MAGIC_8192' in response:
                print("Logging out...\n")
                print("Returning to main menu...\n\n")
                break
            
            print(response)





class Main:

    def __init__(self):
        self.host = '127.0.0.1'
        self.port = 6969


    def RemoteMenu(self, user):
        print("Logged in succesfully!")

        session = SocketSession(self.host, self.port)

        main_menu = session.Connect(user)

        main_menu = str(main_menu, 'utf-8')
        print(main_menu)

        session.ConsoleSession()




    def main(self):

        menu = Menu()
        configfile = '../config.json' # set path to config.jsons
        config = Config(configfile)
        db = Userdb(config)



        while True:
            selection = menu.getselection()

            if selection == 1:
                login_with_email = menu.login_option()
                if login_with_email == None: # when user choose not to login from login option menu
                    continue
                elif login_with_email == 1: # when user choose to login with email
                    email = menu.get_login_detail(True)
                    valid_login = db.login(email, True)
                    if valid_login:
                        # TODO: get username for use with remote menu
                        self.RemoteMenu(email)
                    else:
                        print("Email or password is not correct!")
                elif login_with_email == 2: # when user choose to login with username
                    username = menu.get_login_detail(False)
                    valid_login = db.login(username, False)
                    if valid_login:
                        self.RemoteMenu(username)
                    else:
                        print("Username or password is not correct!")
                elif login_with_email == 3:
                    print("Login with Facial Recognition....")
                    # copy encoding file to current directory
                    copy2('./facialrecognition/encodings.pickle', '.')
                    recognise = Recognise()
                    name = recognise.getuser()
                    valid_login = False
                    if name != "Unknown":
                        valid_login = True
                    if valid_login:
                        self.RemoteMenu(name)
                    else:
                        print("Login failed!")
                    

            elif selection == 2:
                db.createuser()
            elif selection == 3:
                recognise = Recognise()
                user = recognise.getuser()
                self.RemoteMenu(user)

            elif selection == 4:
                qrscan = QRscan()
                book = qrscan.scan()
                print("Book returned: " + book)

            else:
                sys.exit(0)

if __name__ == "__main__":
    Main().main()
