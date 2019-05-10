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
            # Get the connection 
            conn, addr = self.sock.accept()
            print("Got a connection from "+str(addr))

            # Start getting the user info
            user = conn.recv(4096)
            print("The user is "+str(user))
            # Send back the main menu
            conn.sendall(bytes("Shalom, main menu goes here", 'UTF-8')) 

            while True:
                # Start getting the users choice
                user_choice = conn.recv(4096)
                print("Got "+str(user_choice)+" from client")
                # Send back the menu
                conn.sendall(bytes("Shalom, here's another menu", 'UTF-8')) 




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
