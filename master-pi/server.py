#!/usr/bin/python3

import sys
import socket


class SocketSession:
    
    def __init__(self, host, port):
        self.host = host
        self.port = port
    

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
                menu = "\n\n" \
                     + "Welcome! Would you like to\n" \
                     + "1. Search the book catalogue\n" \
                     + "2. Borrow\n" \
                     + "3. Logout\n"
                conn.sendall(bytes(menu, 'UTF-8')) 


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
                            response = 'SEARCHING FOR BOOKS BEEP BOOP BEEP'
                        elif user_choice is '2':
                            response = 'What book would you like to borrow?'
                        elif user_choice is '3':
                            response = 'TERMINATE_MAGIC_8192'
                        else:
                            response = 'Invalid response, please try again :)'
                        


                    # Send back the menu
                    conn.sendall(bytes(response, 'UTF-8')) 
            except:
                print("Connection terminated... Listening again")




class Main:

    def __init__(self):
        self.host = '127.0.0.1' # Loopback for listening on
        self.port = 6969







    def main(self):
        print("Firing up!")

        session = SocketSession(self.host, self.port)

        session.Listen()

         



if __name__ == "__main__":
    Main().main()
