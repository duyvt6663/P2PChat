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
            self.cServer.send(json.dumps(msg).encode('utf-8'))
            lock.release()
            # recv data
            lock.acquire()
            data = self.cServer.recv(1024)
            lock.release()
            data = json.loads(data.decode('utf-8'))
            if data['type'] == RepTag.LOGIN_SUCCESS:
                # login success
                self.friends = data['friendlist']
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
            self.cServer.send(json.dumps(msg).encode('utf-8'))
            lock.release()
            # recv data
            lock.acquire()
            data = self.cServer.recv(1024)
            lock.release()
            data = json.loads(data.decode('utf-8'))
            if data['type'] == RepTag.SIGNUP_SUCCESS:
                # signup success
                # adding gibberish to indicate success
                success.append('hkdhfewo')
        except Exception as e:
            print(repr(e))

    def logoutThread(self):
        # format message to send
        msg = {'type': ReqTag.LOGOUT}
        lock.acquire()
        self.cServer.send(json.dumps(msg).encode('utf-8'))
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
        self.cServer.send(json.dumps(msg).encode('utf-8'))
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
                client.send(json.dumps(msg).encode('utf-8'))
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
                                self.chatSessions[data['id']] = ['--- SESSION INITIATED ---']
                            self.updateAddress(data['id'], data['ip'], data['port'])
                    if not flag:
                        msg = {
                            'type': RepTag.SESSION_REJECT,
                            'destID': data['id']
                        }
                    self.cServer.send(json.dumps(msg).encode('utf-8'))
                elif data['type'] == RepTag.SESSION_ACCEPT:
                    self.updateAddress(data['id'], data['ip'], data['port'])
                    # insert into 1st position of chat session
                    if data['id'] not in self.chatSessions:
                        self.chatSessions[data['id']] = ['--- SESSION INITIATED ---']
                    else:
                        self.chatSessions[data['id']].insert(0, '--- SESSION INITIATED ---')
                        # reset chat box if sender is current chat friend
                        if GUI.currChatFriend.get() == data['id']:
                            GUI.reset_chatbox(data['id'])

                elif data['type'] == ReqTag.SESSION_CLOSE:
                    if data['with'] in self.chatSessions and data['status'] == 'COMPLETELY':
                        self.chatSessions.pop(data['with'])
            except Exception as e:
                print(repr(e))

#   def is_account_exist(self, username):
#     lock.acquire_read()
#     with open('./Server/Users.json', 'r') as file:
#         users = json.load(file)
#     lock.release_read()
#     for i in users:
#         if users[i]['username'].__len__ > 0:
#             return True
#
#     return False
#
# # signup a user
# def sign_up_user(self, user):
#     account = {
#         "nickname": user['nickname'],
#         "username": user['username'],
#         "password": user['password']
#     }
#
#     writeToStorage(lock, account);
#
# # retrieves the password for a given username
# def get_password(self, nickname):
#     lock.acquire_read()
#     with open('./Server/Users.json', 'r') as file:
#         users = json.load(file)
#     lock.release_read()
#
#     for i in users:
#         if users[i]['nickname'] == nickname:
#             return users[i]['password']
#
# # checks if an account with the username online
#
# def is_account_online(self, nickname):
#     if self.online_peers.find({"nickname": nickname}).count() > 0:
#         return True
#     else:
#         return False
#
# # logs in the user
#
# def user_login(self, nickname, ip, port):
#     active_peer = {
#         "nickname": nickname,
#         "ip": ip,
#         "port": port
#     }
#     self.online_peers.update(active_peer);
#
# # logs out the user
#
# def user_logout(self, nickname):
#     self.online_peers.pop({"nickname": nickname})
#
# # retrieves the ip address and the port number of the username
#
# def get_peer_ip_port(self, nickname):
#     retrieve_peer = self.online_peers.find({"nickname": nickname})
#     return (retrieve_peer["ip"], retrieve_peer["port"])
