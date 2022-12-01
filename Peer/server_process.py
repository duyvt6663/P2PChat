# sample code
from socket import *
import pickle
import time
import threading
import random
from os import listdir
from tkinter import *
from tkinter import messagebox


HOST = '127.0.0.1'
PORT = random.randint(1024, 49151)

class ServerProcess:
    serverSocket = None
    def __init__(self):
        self.serverSocket = socket(AF_INET, SOCK_STREAM)
        self.serverSocket.bind((HOST, PORT))
        self.serverSocket.listen(10)
        print("Connecting...")
        self.peerASocket, addrA = self.serverSocket.accept()
        while True:
            conn, addr = self.serverSocket.accept()
            print('Connected ' + str(addr))
            t = threading.Thread(target=self.receive_messages_in_a_new_thread, args = (conn,), daemon = True)
            t.start()
    def receive_messages_in_a_new_thread(self, conn):
        while True:
            try:
                message = conn.recv(1023)
                self.peerASocket.send(message)
            except:
                conn.close()
                break