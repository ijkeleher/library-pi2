#!/usr/bin/python3

import sys
import MySQLdb
import json
import hashlib, binascii, os
import getpass
import re

class Menu:

    def displaymenu(self):
        print("""
        1.Login
        2.Register new user
        3.Exit
        """)

    def getselection(self):
        while True:
            self.displaymenu()

            try:
                selection = int(input("Enter Selection: "))

                if 4 > selection > 0:
                    return selection

            except ValueError:
                print("Error: enter valid selection")
                continue


class Userdb:

    def __init__(self, config):

        self.__conn = MySQLdb.connect(config.gethostname(), config.getdbuser(), config.getdbpass(), config.getdbname())

    def createuser(self):

        inputvalid = False

        chars = re.compile('^[a-zA-Z]+$')
        charsnums = re.compile('^[a-zA-Z0-9]+$')
        emailaddr = re.compile('^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$')

        while not inputvalid:

            username = input("Enter Username: ")

            if re.fullmatch(charsnums, username) is None:
                print("Error: invalid username")
                continue

            passwordraw = getpass.getpass("Enter Password: ")

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

            inputvalid = True

        cursor = self.__conn.cursor()

        params = (username, passwordhashed, firstname, lastname, email)

        cursor.execute("INSERT INTO rpuser(username, password, firstname, lastname, email) VALUES (%s,%s,%s,%s,%s)", params)

        self.__conn.commit()


    def hash_password(password):
        """Reference: https://www.vitoshacademy.com/hashing-passwords-in-python/"""
        salt = hashlib.sha256(os.urandom(60)).hexdigest().encode('ascii')
        pwdhash = hashlib.pbkdf2_hmac('sha512', password.encode('utf-8'), salt, 100000)
        pwdhash = binascii.hexlify(pwdhash)
        return (salt + pwdhash).decode('ascii')

    def verify_password(stored_password, provided_password):
        """Reference: https://www.vitoshacademy.com/hashing-passwords-in-python/"""
        salt = stored_password[:64]
        stored_password = stored_password[64:]
        pwdhash = hashlib.pbkdf2_hmac('sha512', provided_password.encode('utf-8'), salt.encode('ascii'), 100000)
        pwdhash = binascii.hexlify(pwdhash).decode('ascii')
        return pwdhash == stored_password


class Config:

    def __init__(self, filename):
        with open(filename) as data:
            self.__conf = json.load(data)

    def getdbuser(self):
        return self.__conf['dbuser']

    def getdbpass(self):
        return self.__conf['dbpass']

    def getdbname(self):
        return self.__conf['dbname']

    def gethostname(self):
        return self.__conf['hostname']




class Main:

    def main(self):

        menu = Menu()
        configfile = 'config.json'
        config = Config(configfile)
        db = Userdb(config)

        while True:
            selection = menu.getselection()

            if selection == 1:
                pass
            elif selection == 2:
                db.createuser()
            else:
                sys.exit(0)
