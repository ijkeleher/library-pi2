#!/usr/bin/env python3

import unittest
from shutil import copy2
from facialrecognition.recognise import Recognise
import client


class RPTest(unittest.TestCase):
    """
    Unit test for reception pi
    Include two test: test local database connection and login
    """

    def test_db_connection(self):
        """
        Unit test for local database connection on reception pi
        """
        config_file = '../config.json'
        config = client.Config(config_file)
        database = client.Userdb(config)
        self.assertIsNotNone(database)

    def test_login(self):
        """
        Unit test for login function
        """
        config_file = '../config.json'
        config = client.Config(config_file)
        database = client.Userdb(config)

        menu = client.Menu()

        valid_login = False
        auth = True
        not_auth = False

        login_option = menu.login_option()
        if login_option == 1:  # when login with email
            email = menu.get_login_detail(True)
            valid_login = database.login(email, True)
        elif login_option == 2:  # when login with username
            username = menu.get_login_detail(False)
            valid_login = database.login(username, False)
        elif login_option == 3:  # when login with facial recognize
            copy2('./facialrecognition/encodings.pickle', '.')
            recognize = Recognise()
            name = recognize.getuser()
            if name != "Unknown":
                valid_login = True
        elif login_option == 4:  # when choose not to login
            valid_login = False

        if valid_login:
            self.assertEqual(auth, valid_login)
        else:
            self.assertEqual(not_auth, valid_login)


if __name__ == "__main__":
    unittest.main(verbosity=2)
