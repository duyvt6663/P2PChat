# sample code
from socket import *
import time
import threading
import random
from os import listdir
from tkinter import *
from tkinter import messagebox
import json, pickle
from Server.Synchronization import  ReadWriteLock
from utils import getFriends, writeToStorage

lock = ReadWriteLock()
#online_peers = {}
class Client():
    def __init__(self):
        self.online_peers = {}
        pass
    def is_account_exist(self, username):
        lock.acquire_read()
        with open('./Server/Users.json', 'r') as file:
            users = json.load(file)
        lock.release_read()
        for i in users:
            if users[i]['username'].__len__ > 0:
                return True
        
        return False

    # signup a user

    def sign_up_user(self, user):
        account = {
            "nickname": user['nickname'],
            "username": user['username'],
            "password": user['password']
        }
        
        writeToStorage(lock, account);

    # retrieves the password for a given username

    def get_password(self, nickname):
        lock.acquire_read()
        with open('./Server/Users.json', 'r') as file:
            users = json.load(file)
        lock.release_read()

        for i in users:
            if users[i]['nickname'] == nickname:
                return users[i]['password']

        

    # checks if an account with the username online

    def is_account_online(self, nickname):
        if self.online_peers.find({"nickname": nickname}).count() > 0:
            return True
        else:
            return False

    # logs in the user

    def user_login(self, nickname, ip, port):
        active_peer = {
            "nickname": nickname,
            "ip": ip,
            "port": port
        }
        self.online_peers.update(active_peer);


    # logs out the user

    def user_logout(self, nickname):
        self.online_peers.pop({"nickname": nickname})

    # retrieves the ip address and the port number of the username

    def get_peer_ip_port(self, nickname):
        retrieve_peer = self.online_peers.find({"nickname": nickname})
        return (retrieve_peer["ip"], retrieve_peer["port"])
