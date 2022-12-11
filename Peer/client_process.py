# sample code
import socket
from socket import *
import errno
import time
from threading import Thread, Lock
import random
from os import listdir
from tkinter import *
from tkinter import messagebox
import json
import pickle
# from Server.utils import getFriends, writeToStorage
from Deserializer import ReqTag, RepTag, RepData

# lock = ReadWriteLock()
#online_peers = {}

# SHOST = '10.128.105.211'
SHOST = 'localhost'
SPORT = 12345
lock = Lock()


class ClientProc():
    def __init__(self, HOST, PORT, GUI):
        self.friends = []
        self.chatSessions = {}
        self.id = -1
        self.nickname = ''
        self.HOST = HOST  # server proc HOST
        self.PORT = PORT  # server proc PORT
        # socket to connect to main server
        self.cServer = socket(AF_INET, SOCK_STREAM)
        self.cServer.settimeout(2)
        self.cServer.connect((SHOST, SPORT))

        # set client thread listening to main server
        sthread = Thread(target=self.listeninServerThread,
                         args=(GUI,), daemon=True)
        sthread.start()

    def loginThread(self, username, password, success):
        try:
            # set message to send back
            msg = {
                'type': ReqTag.LOGIN,
                'username': username,
                'password': password
            }
            # use main server socket
            lock.acquire()
            self.cServer.sendall(json.dumps(msg).encode('utf-8'))
            lock.release()
            # recv data
            lock.acquire()
            data = self.cServer.recv(1024)
            lock.release()
            data = json.loads(data.decode('utf-8'))
            if data['type'] == RepTag.LOGIN_SUCCESS:
                # login success
                if self.id == -1:  # 1st login
                    self.friends = data['friendlist']
                elif self.id != data['id']:  # not 1st login, different acc
                    self.friends = data['friendlist']
                    self.chatSessions = {}  # flush chat sessions
                # print(self.friends)
                # the final case is not 1st login, same acc -> do nothing

                self.id = data['id']
                self.nickname = data['nickname']
                # adding gibberish to indicate success
                success.append('324hi2932jj')
        except Exception as e:
            print(repr(e))

    def signupThread(self, username, password, nickname, success):
        try:
            # set message to send back
            msg = {
                'type': ReqTag.SIGNUP,
                'username': username,
                'password': password,
                'nickname': nickname
            }
            # use main server socket
            lock.acquire()
            self.cServer.sendall(json.dumps(msg).encode('utf-8'))
            lock.release()
            # recv data
            lock.acquire()
            data = self.cServer.recv(1024)
            lock.release()
            data = json.loads(data.decode('utf-8'))
            if data['type'] == RepTag.SIGNUP_SUCCESS:
                # set nickname
                if self.id != -1:  # not 1st time
                   self.friends = []
                self.id = data['id']
                self.nickname = nickname
                # adding gibberish to indicate success
                success.append('hkdhfewo')
        except Exception as e:
            print(repr(e))

    def logoutThread(self):
        # format message to send
        msg = {'type': ReqTag.LOGOUT}
        lock.acquire()
        self.cServer.sendall(json.dumps(msg).encode('utf-8'))
        lock.release()

    def openSessionThread(self, peerID):
        # set message to request session
        msg = {
            'type': ReqTag.SESSION_OPEN,
            'destID': peerID,
            'ip': self.HOST,
            'port': self.PORT
        }
        lock.acquire()
        self.cServer.sendall(json.dumps(msg).encode('utf-8'))
        lock.release()
    def sendChatThread(self, message, peerID):
        msg = {
            'type': RepData.MESSAGE,
            'src': self.id,
            'data': message
        }
        client = socket(AF_INET, SOCK_STREAM)
        for friend in self.friends:
            if friend['id'] == peerID:
                client.connect((friend['ip'], friend['port']))
                client.sendall(json.dumps(msg).encode('utf-8'))
                client.close()

    def sendFileThread(self, friendID, file_path):
        # send file
        if (file_path and file_path != None and file_path != ''):
            filename = file_path.split('/').pop()
            # send the file
            client = socket(AF_INET, SOCK_STREAM)
            for friend in self.friends:
                if friend['id'] == friendID:
                    client.connect((friend['ip'], friend['port']))
                    # chop the message into multiple parts and send
                    file = open(file_path, 'rb')

                    i = -1 # init offset
                    line = ("0"*1025).encode('utf-8') # init a b string of length >= 900
                    while len(line) >= 900: # cap at 900 bytes because json format takes extra bytes
                        line = file.read(900)
                        i = -1 if len(line) < 900 else i + 1
                        msg = {
                            'type': RepData.FILE,
                            'src': self.id,
                            'data': line.decode(),
                            'offset': i,
                            'name': filename
                        }
                        client.sendall(json.dumps(msg).encode('utf-8'))
                        time.sleep(.1)
                    print('file sent')
                    client.close()

    def updateAddress(self, friendID, ip, port):
        for friend in self.friends:
            if friend['id'] == friendID:
                friend['ip'] = ip
                friend['port'] = port

    def listeninServerThread(self, GUI):
        while True:
            try:
                data = self.cServer.recv(1024)
                data = json.loads(data.decode('utf-8'))
            except OSError: # catch time out here
                continue
            except Exception as e:
                # Something else happened, handle error, exit, etc.
                print(repr(e))
                return
            try:
                # do friend status update
                if data['type'] == RepTag.ONLINE:
                    for friend in self.friends:
                        if friend['id'] == data['friend']:
                            friend['status'] = 'ONLINE'
                            GUI.update_friend_box()
                elif data['type'] == RepTag.OFFLINE:
                    for friend in self.friends:
                        if friend['id'] == data['friend']:
                            friend['status'] = 'OFFLINE'
                            GUI.update_friend_box()
                elif data['type'] == ReqTag.SESSION_OPEN:
                    flag = False
                    for friend in self.friends:
                        if friend['id'] == data['id']:
                            flag = True
                            msg = {
                                'type': RepTag.SESSION_ACCEPT,
                                'destID': data['id'],
                                'ip': self.HOST,
                                'port': self.PORT
                            }
                            if data['id'] not in self.chatSessions:
                                # init a session cache
                                self.chatSessions[data['id']] = ['--- SESSION INITIATED ---']
                            self.updateAddress(data['id'], data['ip'], data['port'])
                    if not flag:
                        msg = {
                            'type': RepTag.SESSION_REJECT,
                            'destID': data['id']
                        }
                    self.cServer.sendall(json.dumps(msg).encode('utf-8'))
                elif data['type'] == RepTag.SESSION_ACCEPT:
                    self.updateAddress(data['id'], data['ip'], data['port'])
                    # insert into 1st position of chat session
                    if data['id'] not in self.chatSessions:
                        self.chatSessions[data['id']] = ['--- SESSION INITIATED ---']
                    else:
                        # initiation success inserted to slot 0 of cache
                        self.chatSessions[data['id']].insert(0, '--- SESSION INITIATED ---')
                        # reset chat box if sender is current chat friend
                        if GUI.currChatFriend.get() == data['id']:
                            GUI.reset_chatbox(data['id'])

                elif data['type'] == ReqTag.SESSION_CLOSE:
                    if data['with'] in self.chatSessions and data['status'] == 'COMPLETELY':
                        self.chatSessions.pop(data['with'])
            except Exception as e:
                print(repr(e))
