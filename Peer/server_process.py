# sample code
from socket import *
import pickle
import time
from threading import Thread
import random
from os import listdir
from tkinter import *
from tkinter import messagebox
from Deserializer import *
import json
from client_process import ClientProc


class ServerProc:
    path = 'C:\\Users\\WIN\\Documents\\GitHub\\P2P-Chat\\Peer\\Files\\'
    def __init__(self, HOST, PORT, client, GUI):
        self.HOST = HOST
        self.PORT = PORT
        thread = Thread(target=self.mainThread, args=(client, GUI), daemon=True)
        thread.start()

    def isFriend(self, client, id):
        for friend in client.friends:
            if friend['id'] == id:
                return True
        return False

    def isSufficient(self, keys):
        if (keys[0] != 0 and keys[0] != -1) or\
           sum([keys[k+1]==keys[k]+1 for k in
                range(len(keys)-1)]) != len(keys)-1:
            return False
        return True

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
        buffer = {}
        while True:
            try:
                msg = conn.recv(1024)
                msg = json.loads(msg.decode('utf-8'))
            except Exception as e:
                print(repr(e))
                return
            try:
                fromPeer().load(msg)
                if not self.isFriend(client, msg['src']):
                    raise 'not friend'
                if msg['type'] == RepData.MESSAGE:
                    # change msg nickname if overlapping with current nickname
                    nickname, content = msg['data'].split(':', 1)
                    if nickname == client.nickname:
                        msg['data'] = nickname + '*: ' + content
                    client.chatSessions[msg['src']].append(msg['data'])
                    # update on UI if currently chatting with this friend
                    if GUI.currChatFriend.get() == msg['src']:
                        GUI.insertchatbox(msg['data'])

                elif msg['type'] == RepData.FILE:
                    peerFile().load(msg)
                    if msg['offset'] == 0:
                        buffer[msg['name']] = {}
                        buffer[msg['name']][0] = msg['data']
                    elif msg['offset'] == -1:
                        # End of file -> flush buffer, write data
                        filename = msg['name']
                        if msg['name'] not in buffer:
                            fileData = msg['data']
                        else:
                            fileData = ''.join(list(buffer[msg['name']].values()))+msg['data']
                            # check if there is sufficient fragments
                            keys = list(buffer[msg['name']].keys())
                            if not self.isSufficient(keys):
                                raise 'insufficient fragments'
                            # clear buffer
                            buffer.pop(filename)

                        # Change file name if already existing
                        if msg['name'] in listdir(self.path):
                            i = 1  # new index for name
                            filex = filename.split('.')
                            newName = filex[0] + '(' + str(i) + ').' + filex[1]
                            while newName in listdir(self.path):
                                i = i + 1
                                newName = filex[0] + '(' + str(i) + ').' + filex[1]
                            filename = newName

                        file = open(self.path + filename, 'wb')
                        file.write(fileData.encode())
                        file.close()

                        for friend in client.friends:
                            if friend['id'] == msg['src']:
                                pad = '' if friend['nickname'] != client.nickname else '*'
                                chatdata = friend['nickname'] + pad + ': SEND ' + filename
                                client.chatSessions[friend['id']] += [chatdata]
                                if GUI.currChatFriend.get() == msg['src']:
                                    GUI.insertchatbox(chatdata)
                    else:
                        buffer[msg['name']][msg['offset']] = msg['data']
            except Exception as e:
                print(repr(e))
