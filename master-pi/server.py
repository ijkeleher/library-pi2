#!/usr/bin/python3

import sys
import socket
import MySQLdb
import json
import hashlib, binascii, os
import getpass
import re
from datetime import datetime
from gcalender import gcalender 

class Clouddb:
	def __init__(self, config):
		self.__conn = MySQLdb.connect(config.gethostname(), config.getdbuser(), config.getdbpass(), config.getdbname())
		self.email_addr = re.compile(r'^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$')


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

	def search(self, query):
		"""
		Search the cloud SQL database for books
		Param:
			query: the string to search for
		Return:
			'' if the search matched 0 books
			otherwise a list of tuples of book data
		"""
		cursor = self.__conn.cursor()
		q = "%"+query+"%"
		cursor.execute("SELECT * FROM Book WHERE UPPER(Title) LIKE UPPER(%s) OR UPPER(Author) LIKE UPPER(%s) OR UPPER(PublishedDate) LIKE UPPER(%s) OR ISBN LIKE %s", [q, q, q, q])
		data = cursor.fetchall()
		if data is not None:
			return data
		else:
			return ''
    
	def borrow(self, book_id, calender):
		"""
		Borrow a book from the SQL database for books and add google calender reminder
		Param:
			book_id: the ID of the book to borrow
		Return:
			'' if book doesn't exist
			otherwise a string of the books name
		"""


		# Get the book name also checking if it exists in the process
		cursor = self.__conn.cursor()
		cursor.execute("SELECT * FROM Book WHERE BookID=%s", [book_id])
		data = cursor.fetchone() # We're searching for a primary key
		
		# The book exists
		if data is not None:
			book_name = data[1] + " by " + data[2]

			print("Borrowing book "+str(book_name))
			event_id = calender.insert(book_name)

			cursor.execute("INSERT INTO BookBorrowed (LMSUserID, BookID, Status, BorrowedDate, EventID) VALUES (%s, %s, %s, %s, %s)", [1, book_id, "borrowed", datetime.now().strftime('%Y-%m-%d'), event_id])
			self.__conn.commit()



			return book_name

		# The book does not exists
		else:
			print("Can't find book with ID "+str(book_id))
			return ''

	def return_book(self, book_id, calender):
		"""
		Return a book from the SQL database for books and delete google calender reminder
		Param:
			book_id: the ID of the book to borrow
		Return:
			'' if book doesn't exist
			otherwise a string 'success'
		"""


		# Get the book name also checking if it exists in the process
		cursor = self.__conn.cursor()
		cursor.execute("SELECT EventID, BookBorrowedID FROM BookBorrowed WHERE BookID=%s AND Status=%s", [book_id, "borrowed"])
		data = cursor.fetchone()
		
		event_id = data[0]
		book_borrow_id = data[1]
		
		# The book exists
		if data is not None and event_id is not None:

			print("Deleting event "+str(event_id))
			calender.delete(event_id)

			cursor.execute("UPDATE BookBorrowed SET Status=%s WHERE BookBorrowedID=%s", ["returned", book_borrow_id])
			self.__conn.commit()



			return 'Success'

		# The book does not exists
		else:
			print("Can't find book with ID "+str(book_id))
			return ''

class Config:

	def __init__(self, filename):
		try:
			with open(filename) as data:
				self.__conf = json.load(data)
		except EnvironmentError:
			print("Can't open "+ filename)

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

	def __init__(self, host, port, db, calender):
		self.host = host
		self.port = port
		self.db = db
		self.calender = calender


	def Listen(self):
		print("Running server on " + self.host+":"+str(self.port))


		# Connect
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
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
					 + "3. QR Code Return Book\n" \
					 + "4. Logout\n"
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
							response = 'What is the ID of the book you wish to borrow?'
							menu = 'borrow'
						elif user_choice is '3':
							response = 'QR_CODE_8192'
							menu = 'qr'
						elif user_choice is '4':
							response = 'TERMINATE_MAGIC_8192'
						else:
							response = 'Invalid response, please try again :)'
					elif menu is 'book':
						print("Processing book search")
						response = 'Found books:\n'


						books = self.db.search(user_choice)

						if books is '':
							results = "No books found :^( sorry fam\n"
						else:
							for book in books:
								response += str(book[1]).ljust(32) + " by " + str(book[2]).ljust(20) + " ISBN: " + str(book[4]) + "\t Book ID: " + str(book[0]) + "\n"


						menu = 'main'
						response += "\nReturning to main menu\n"
						response += menutext

					elif menu is 'qr':
						self.db.return_book(user_choice, self.calender)
						response = 'Book returned! Book = '+user_choice
						response += menutext
						menu = 'main'
					elif menu is 'borrow':

						# TODO: Validate input
						book_id = int(user_choice)

						print("Attempting to borrow "+str(book_id)+" which is "+str(type(book_id)))
						
						book_name = self.db.borrow(book_id, self.calender)
					
						if book_name is '':
							response = 'Failed to find that book :(\n'
						else:
							response = 'Book borrowed!'

						response += menutext
						menu = 'main'



					# Send back the menu
					conn.sendall(bytes(response, 'UTF-8'))
			except ValueError:
				print("Connection terminated... Listening again")
			except BrokenPipeError:
				print("Connection terminated... Listening again")
			except ConnectionResetError:
				print("Connection terminated... Listening again")


class Speech2Text:
    def record(self):
        pass


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

		calender = gcalender()

		session = SocketSession(self.host, self.port, db, calender)

		session.Listen()



if __name__ == "__main__":
	Main().main()
