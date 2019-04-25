#!/usr/bin/python3

import sys
import MySQLdb
import json

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
        pass

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
