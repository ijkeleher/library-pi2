#!/usr/bin/python3

import binascii
import getpass
import hashlib
import json
import os
import re
import socket
import sys
from shutil import copy2

import MySQLdb
from facialrecognition.recognise import Recognise
from qrscan import QRscan
from speech import Speech2Text


class Menu:
    """
    local client menu
    provide function for user to login, register
    """

    def displaymenu(self):
        """
        print out menu to console
        """
        print("1.Login\n2.Register new user\n3.Exit")

    def getselection(self):
        """
        For user to make selection
        Return:
            selection: user's selection to interact to menu
        except:
            ValueError: when user enter non-digital or number beyond the range
            EOFError: end of file error
        """
        while True:
            self.displaymenu()

            try:
                selection = int(input("Enter Selection: "))

                if 4 > selection > 0:
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
    """
    Local database store user's information
    contains: username, salted password, firstname, lastname, email
    """

    def __init__(self, config):
        """
        constructor
        Parma:
            config: local database config
        """
        self.__conn = MySQLdb.connect(config.gethostname(), config.getdbuser(), config.getdbpass(), config.getdbname())
        self.email_addr = re.compile(r'^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$')

    def createuser(self):
        """
        create user and insert new user to local database
        """

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

        cursor.execute("INSERT INTO rpuser(username, password, firstname, lastname, email) VALUES (%s,%s,%s,%s,%s)",
                       params)

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
        """
        convert plaintext password into encrypted password
        Parma:
            password: plaintext password
        Return:
            salted password
        Reference: https://www.vitoshacademy.com/hashing-passwords-in-python/
        """
        salt = hashlib.sha256(os.urandom(60)).hexdigest().encode('ascii')
        pwdhash = hashlib.pbkdf2_hmac('sha512', password.encode('utf-8'), salt, 100000)
        pwdhash = binascii.hexlify(pwdhash)
        return (salt + pwdhash).decode('ascii')

    def verify_password(self, stored_password, provided_password):
        """
        check if provided password match with stored password
        Parma:
            stored_password: salted password stored in database
            provided_password: password that need to be compared with
        Return:
            True if two password match
            False otherwise
        Reference: https://www.vitoshacademy.com/hashing-passwords-in-python/
        """
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
    """
    config for local environment
    """

    def __init__(self, filename):
        try:
            with open(filename) as data:
                self.__conf = json.load(data)
        except EnvironmentError:
            print("Can't open " + filename)

    def getdbuser(self):
        """
        get database username
        Return:
            database username
        """
        return self.__conf['dbuser']

    def getdbpass(self):
        """
        get database user password
        Return:
            database uesr password
        """
        return self.__conf['dbpass']

    def getdbname(self):
        """
        get database name
        Return:
            database name
        """
        return self.__conf['dbname']

    def gethostname(self):
        """
        get hostname
        Return:
            hostname
        """
        return self.__conf['hostname']


class SocketSession:
    """
    Socket session which allow reception-pi and master-pi communicate with each other
    """

    def __init__(self, host, port):
        self.host = host
        self.port = port

    def Connect(self, user):
        """
        connect to master pi using socket
        Parma:
            user: logged in user
        Return:
            menu for user to interact with
        """
        print("Establishing connection to remote host @ " + self.host + ":" + str(self.port))

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
        """
        Console session allow user to interact with remote sessib
        """

        excase = False

        while True:

            if not excase:
                # Get some user input
                inp = str(input("Please enter your response: "))
                if not inp:
                    inp = None
                if inp is None:
                    print("Invalid response!")
                    continue

                # Shoot it off to the server
                self.sock.sendall(bytes(inp, 'UTF-8'))

            excase = False

            # Get the response
            response = str(self.sock.recv(4096), 'utf-8')
            if 'Please enter a book title' in response:
                try:
                    selection = int(input("Please select searching method:\n" +
                                          "1. Input book detail\n" +
                                          "2. Voice search\n"))
                    if selection == 1:
                        book_name = input("Book name: ")
                        self.sock.sendall(bytes(book_name, 'UTF-8'))
                    elif selection == 2:
                        print("Listening...\n")
                        speech = Speech2Text()
                        book_name = speech.record()
                        if book_name is None:
                            book_name = "THISISNOTGONNAMATCHANYTHING"
                        self.sock.sendall(bytes(book_name, 'UTF-8'))
                except ValueError:  # try catch for selection input
                    print("Invalid Option")
                    self.sock.sendall(bytes('THISISNOTGONNAMATCHANYTHING', 'UTF-8'))

                excase = True

            if 'QR_CODE_8192' in response:
                print("QR CODE Scanner\n")
                qrcode = QRscan()
                book_code = qrcode.scan()
                self.sock.sendall(bytes(book_code, 'utf-8'))
                excase = True

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
        """
        Connect to Master Pi for borrow, return book options
        Param:
            uesr: user that logged in
        """
        print("Logged in succesfully!")

        session = SocketSession(self.host, self.port)

        main_menu = session.Connect(user)

        main_menu = str(main_menu, 'utf-8')
        print(main_menu)

        session.ConsoleSession()

    def main(self):

        menu = Menu()
        configfile = '../config.json'  # set path to config.jsons
        config = Config(configfile)
        db = Userdb(config)

        while True:
            selection = menu.getselection()

            if selection == 1:
                login_method = menu.login_option()
                if login_method == None:  # when user choose not to login from login option menu
                    continue
                elif login_method == 1:  # when user choose to login with email
                    email = menu.get_login_detail(True)
                    valid_login = db.login(email, True)
                    if valid_login:
                        self.RemoteMenu(email)
                    else:
                        print("Email or password is not correct!")
                elif login_method == 2:  # when user choose to login with username
                    username = menu.get_login_detail(False)
                    valid_login = db.login(username, False)
                    if valid_login:
                        self.RemoteMenu(username)
                    else:
                        print("Username or password is not correct!")
                elif login_method == 3:
                    print("Login with Facial Recognition....")
                    # copy encoding file to current directory
                    copy2('./facialrecognition/encodings.pickle', '.')
                    recognise = Recognise()
                    name = recognise.getuser()
                    valid_login = False
                    if name is not "Unknown":
                        valid_login = True
                    if valid_login:
                        self.RemoteMenu(name)
                    else:
                        print("Login failed!")


            elif selection == 2:
                db.createuser()
            else:
                sys.exit(0)


if __name__ == "__main__":
    Main().main()
