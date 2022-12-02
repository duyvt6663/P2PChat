# sample code
from socket import *
import pickle
import time
from threading import Thread
import random
from os import listdir
from tkinter import *
from tkinter import messagebox


class ServerProc:
    def __init__(self, HOST, PORT):
        self.server = socket(AF_INET, SOCK_STREAM)
        self.server.bind((HOST, PORT))
        self.server.listen(10)
        # accept client proc to communicate
        self.clientSocket, _ = self.server.accept()

        thread = Thread(target=self.mainThread, daemon=True)
        thread.start()

    def mainThread(self):
        while True:
            conn, addr = self.server.accept()
            print('Connected to: ', str(addr[0]), ': ', str(addr[1]))
            t = Thread(target=self.listeninThread, args=(conn,), daemon=True)
            t.start()
    def listeninThread(self, conn):
        while True:
            try:
                message = conn.recv(1023)
                self.clientSocket.send(message)
            except:
                conn.close()
                break