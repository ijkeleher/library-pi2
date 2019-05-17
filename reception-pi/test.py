#!/usr/bin/env python3

import unittest
import Client


class RPTest(unittest.TestCase):
    def test_db_connection(self):
        config_file = '../config.json'
        config = Client.Config(config_file)
        db = Client.Userdb(config)
        self.assertIsNotNone(db)

    def test_login(self):
        config_file = '../config.json'
        config = Client.Config(config_file)
        db = Client.Userdb(config)

        provided_pwd = "admin123"
        hashed_pwd = db.hash_password(provided_pwd)
        self.assertTrue(db.verify_password(hashed_pwd, provided_pwd))

    # TODO: test register new user on local db
    def test_register(self):
        config_file = '../config.json'
        config = Client.Config(config_file)
        db = Client.Userdb(config)
        
        connection = db._Userdb__conn
        cursor = connection.cursor()

        user_count = cursor.execute("""SELECT * FROM rpuser""")
        print("\n" + str(user_count))

if __name__ == "__main__":
    unittest.main(verbosity=2)