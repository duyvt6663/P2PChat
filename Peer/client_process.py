# sample code
from socket import *
import time
from threading import Thread, Lock
import random
from os import listdir
from tkinter import *
from tkinter import messagebox
import json, pickle
# from Server.utils import getFriends, writeToStorage
from Deserializer import ReqTag, RepTag

# lock = ReadWriteLock()
#online_peers = {}

SHOST = 'localhost'
SPORT = 12345
lock = Lock()
class ClientProc():
    def __init__(self,HOST,PORT):
        self.friends = []
        # socket to connect to server proc
        self.pServer = socket(AF_INET, SOCK_STREAM)
        self.pServer.connect((HOST, PORT))
        # socket to connect to main server
        self.cServer = socket(AF_INET, SOCK_STREAM)
        self.cServer.connect((SHOST, SPORT))
        # set client thread listening to main server
        sthread = Thread(target=self.listeninServerThread, daemon=True)
        sthread.start()
        # set client thread listening to server proc/other peers
        pthread = Thread(target=self.listeninPeerThread, daemon=True)
        pthread.start()

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
                success.append('324hi2932jj') # adding gibberish to indicate success
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
            data = self.cServer.recv(1024)
            data = json.loads(data.decode('utf-8'))
            if data['type'] == RepTag.SIGNUP_SUCCESS:
                # signup success
                success.append('hkdhfewo')  # adding gibberish to indicate success
        except Exception as e:
            print(repr(e))

    def listeninServerThread(self):
        while True:
            try:
                lock.acquire()
                data = self.cServer.recv(1024)
                lock.release()
                data = json.loads(data.decode('utf-8'))
            except:
                print('Disconnected to server')
                return
            try:
                # excluding login, session-related response,
                # only do serverProc msg and friend status update
                print('hello')
            except Exception as e:
                print(repr(e))

    def listeninPeerThread(self):
        # message passed down from server proc
        while True:
            try:
                lock.acquire()
                data = self.pServer.recv(1024)
                lock.release()
                data = json.loads(data.decode('utf-8'))
            except:
                print('Disconnected to server')
                return
            try:
                # excluding login, session-related response,
                # only do serverProc msg and friend status update
                print('hello')
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
