#!/usr/bin/python3

import sys
import socket
import MySQLdb
import json
import hashlib, binascii, os
import getpass
import re

class Clouddb:

	def __init__(self, config):
		self.__conn = MySQLdb.connect(config.gethostname(), config.getdbuser(), config.getdbpass(), config.getdbname())
		self.email_addr = re.compile('^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$')


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

	def search(self, query, queryType):
		"""
		Sear
		Param:
			detail: login detail, either username or email
			email_login: True if user choose to login with email, False if user choose to login with username
		Return:
			True if login is valid
			False otherwise
		"""
		cursor = self.__conn.cursor()
		cursor.execute("SELECT * FROM Book WHERE Title LIKE %s", ["%"+query+"%"])
		data = cursor.fetchall()
		if data is not None:
			return data
		else:
			return ''


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
	
	def __init__(self, host, port, db):
		self.host = host
		self.port = port
		self.db = db
	

	def Listen(self):
		print("Running server on " + self.host+":"+str(self.port))
	  

		# Connect
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
		self.sock.bind((self.host, self.port))
		self.sock.listen()

		
		# Don't worry about threading as only one reception pi for moment
		while True:
			try:
				# Get the connection 
				conn, addr = self.sock.accept()
				print("Got a connection from "+str(addr))

				# Start getting the user info
				user = conn.recv(4096)
				print("The user is "+str(user))
				# Send back the main menu
				menutext = "\n\n" \
					 + "Welcome! Would you like to\n" \
					 + "1. Search the book catalogue\n" \
					 + "2. Borrow\n" \
					 + "3. Logout\n"
				conn.sendall(bytes(menutext, 'UTF-8')) 


				menu = 'main'
				while True:
					# Send this to the user at the end of the method
					response = "An error happened on the server"


					# Start getting the users choice
					user_choice = str(conn.recv(4096), 'utf-8')
					print("Got "+user_choice+" from client")

					if menu is 'main':
						print("Processing main menu choice")
						if user_choice is '1':
							response = 'Please enter a book title'
							menu = 'book'
						elif user_choice is '2':
							response = 'What book would you like to borrow?'
						elif user_choice is '3':
							response = 'TERMINATE_MAGIC_8192'
						else:
							response = 'Invalid response, please try again :)'
					elif menu is 'book':
						response = 'Found books:\n'

						
						books = self.db.search(user_choice, "author")
						
						if books is '':
							results = "No books found :^( sorry fam\n"
						else:
							for book in books:
								response += str(book[1]) + " by " + str(book[2]) + " ISBN: " + str(book[4])+"\n"
						
						
						menu = 'main'
						response += "\nReturning to main menu\n"
						response += menutext
						


					# Send back the menu
					conn.sendall(bytes(response, 'UTF-8')) 
			except ValueError:
				print("Connection terminated... Listening again")
			except BrokenPipeError:
				print("Connection terminated... Listening again")




class Main:

	def __init__(self):
		self.host = '127.0.0.1' # Loopback for listening on
		self.port = 6969

	def main(self):
		print("Firing up!")

		# Connect to database
		configfile = '../config_cloud.json'
		config = Config(configfile)
		db = Clouddb(config)
		print("Connected to cloud SQL instance!")
		

		session = SocketSession(self.host, self.port, db)

		session.Listen()



if __name__ == "__main__":
	Main().main()
