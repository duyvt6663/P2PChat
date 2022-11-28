# import socket programming library
import json
import socket
# import thread module
from _thread import *
import threading
from threading import Thread
# import serializer
from Deserializer import ClientSchema, SignUpSchema, LoginAuthenSchema, ReqTag
from utils import hashmap, getFriends

print_lock = threading.Lock()
clients = {}

# peer handling function
def peerConnection(conn,addr):
    try:
        data = json.loads(conn.recv(1024))
        client = ClientSchema().load(data)
        # connection set
        if client['type'] == ReqTag.LOGIN:
            # login authenication
            LoginAuthenSchema().load(data)
            friendlist = getFriends(client['username'], clients)
            conn.send(json.dumps({'type':'LOGIN',
                                  'message':'SUCCESS'}))
            conn.send(json.dumps(friendlist))  # send back friendlist
        else: # sign up validation
            SignUpSchema().load(data)
            # add to hashmap
            # add to Users.json
            msg = {'type': 'SIGNUP',
                   'message': 'SUCCESS'}
            conn.send(json.dumps(msg)) # notify success

        # add id to client list; can log in multiple instances simultaneously
        id = hashmap[client['username']]
        if id not in clients:
            clients[id] = conn

        # broadcast online status to online friends
        with open('Users.json', 'r') as openfile:
            users = json.load(openfile)
        for friend in users[id]['friends']:
            if friend in clients:
                conn.send(json.dumps({'type': 'ONLINE',
                                      'friend': id}))
    except Exception as e:
        conn.send(json.dumps({"type": "ERROR",
                              "message": {e.message}}))
        print('Connection closed with :', addr[0], ':', addr[1])
        conn.close()

    # wait for session or disconnect
    while True:
        try:
            data = json.loads(conn.recv(1024))
            req = someclass().load(data)
            if req['type'] == ReqTag.SESSION_OPEN:
            elif req['type'] == ReqTag.SESSION_REJECT:
            elif req['type'] == ReqTag.SESSION_ACCEPT:
            elif req['type'] == ReqTag.LOGOUT:

    # connection closed
    conn.close()


# main server thread
if __name__ == '__main__':
    host = ""
    port = 12345  # reserve a port on your computer
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    print("socket binded to port", port)

    # put the socket into listening mode
    server.listen(5)
    print("socket is listening")

    # a forever loop until client wants to exit
    while True:
        # establish connection with client
        conn, addr = server.accept()

        # lock acquired by client
        print_lock.acquire()
        print('Connected to :', addr[0], ':', addr[1])

        # Start a new thread and return its identifier
        Thread(target=peerConnection, args=(conn, addr))
    # server.close()