# sample code
from socket import *
import pickle
import time
from threading import Thread
import random
from os import listdir
from tkinter import *
from tkinter import messagebox
from Deserializer import peerMessage, RepData
import json


class ServerProc:
    def __init__(self, HOST, PORT, client):
        thread = Thread(target=self.mainThread, args=(HOST, PORT, client))
        thread.start()

    def mainThread(self, HOST, PORT, client):
        self.server = socket(AF_INET, SOCK_STREAM)
        self.server.bind((HOST, PORT))
        self.server.listen(10)  # blocking function -> different thread
        while True:
            conn, addr = self.server.accept()
            print('Connected to: ', str(addr[0]), ': ', str(addr[1]))
            t = Thread(target=self.listeninPeerThread, args=(conn, client), daemon=True)
            t.start()

    def listeninPeerThread(self, conn, client):
        while True:
            try:
                msg = conn.recv(1024)
                msg = json.loads(msg.decode('utf-8'))
            except:
                #
                return
            try:
                if msg['type'] == RepData.MESSAGE:
                    peerMessage().loads(msg)
                    client.chatSessions[msg['id']].append(msg['data'])
                    # update on UI if currently chatting with this friend

            except Exception as e:
                print(repr(e))
