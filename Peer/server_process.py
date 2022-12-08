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
    def __init__(self, HOST, PORT, client, GUI):
        self.HOST = HOST
        self.PORT = PORT
        thread = Thread(target=self.mainThread, args=(client, GUI), daemon=True)
        thread.start()

    def mainThread(self, client, GUI):
        self.server = socket(AF_INET, SOCK_STREAM)
        self.server.bind((self.HOST, self.PORT))
        self.server.listen(10)  # blocking function -> different thread
        while True:
            conn, addr = self.server.accept()
            print('Connected to: ', str(addr[0]), ': ', str(addr[1]))
            t = Thread(target=self.listeninPeerThread, args=(conn, client, GUI), daemon=True)
            t.start()

    def listeninPeerThread(self, conn, client, GUI):
        while True:
            try:
                msg = conn.recv(1024)
                msg = json.loads(msg.decode('utf-8'))
            except:
                return
            try:
                # print(f'message: ${msg}')
                if msg['type'] == RepData.MESSAGE:
                    peerMessage().load(msg)
                    client.chatSessions[msg['src']].append(msg['data'])
                    # update on UI if currently chatting with this friend
                    if GUI.currChatFriend.get() == msg['src']:
                        GUI.insertchatbox(msg['data'])

            except Exception as e:
                print(repr(e))
