# sample code
from socket import *
import time
from threading import Thread, Lock
import random
from os import listdir
from tkinter import *
from tkinter import messagebox
import json
import pickle
# from Server.utils import getFriends, writeToStorage
from Deserializer import ReqTag, RepTag

# lock = ReadWriteLock()
#online_peers = {}

SHOST = 'localhost'
SPORT = 12345
lock = Lock()


class ClientProc():
    def __init__(self, HOST, PORT, GUI):
        self.friends = []
        self.chatSessions = {}
        # socket to connect to main server
        self.cServer = socket(AF_INET, SOCK_STREAM)
        self.cServer.connect((SHOST, SPORT))
        self.cServer.setblocking(False)
        self.cServer.settimeout(5)
        # set client thread listening to main server
        sthread = Thread(target=self.listeninServerThread,
                         args=(self, GUI), daemon=True)
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
            'destID': peerID
        }
        lock.acquire()
        self.cServer.send(json.dumps(msg).encode('utf-8'))
        lock.release()

    def listeninServerThread(self, GUI):
        while True:
            try:
                data = self.cServer.recv(1024)
                data = json.loads(data.decode('utf-8'))
            except:
                print('Disconnected to server')
                return
            try:
                # do friend status update
                if data['type'] == RepTag.ONLINE:
                    for i in self.friends:
                        if self.friends[i]['id'] == data['id']:
                            self.friends[i]['status'] = 'ONLINE'
                            GUI.update_friend_box()
                elif data['type'] == RepTag.OFFLINE:
                    for i in self.friends:
                        if self.friends[i]['id'] == data['id']:
                            self.friends[i]['status'] = 'OFFLINE'
                            GUI.update_friend_box()
                elif data['type'] == ReqTag.SESSION_OPEN:
                    flag = False
                    for i in self.friends:
                        if self.friends[i]['id'] == data['destID']:
                            flag = True
                            msg = {
                                'type': RepTag.SESSION_ACCEPT,
                                'destID': data['destID']
                            }
                            self.chatSessions[data['destID']] = ['--- SESSION INITIATED ---']
                    if not flag:
                        msg = {
                            'type': RepTag.SESSION_REJECT,
                            'destID': data['destID']
                        }
                    self.cServer.send(json.dumps(msg).encode('utf-8'))
                elif data['type'] == ReqTag.SESSION_CLOSE:
                    if data['with'] in self.chatSessions and data['tag'] == 'COMPLETELY':
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
