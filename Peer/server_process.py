# sample code
from socket import *
import pickle
import time
import threading
import random
from os import listdir
from tkinter import *
from tkinter import messagebox


class ServerProcess:
    HOST = '127.0.0.1'
    PORT = random.randint(1024, 49151)
    server = None
    def __init__(self):
        self.server = socket(AF_INET, SOCK_STREAM)
        self.server.bind((self.HOST, self.PORT))
        self.server.listen(10)
        print("Connecting...")
        self.peerASocket, addrA = self.server.accept()
        while True:
            conn, addr = self.server.accept()
            # check if session already exists: client B -> server A, client A -> server B
            #conn.close()
            print('Connected to: ', str(addr[0]), ': ', str(addr[1]))
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