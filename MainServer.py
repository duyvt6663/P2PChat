# import socket programming library
import json
import socket
# import thread module
from _thread import *
import threading
from threading import Thread
# import serializer
from Deserializer import RequestSchema, ClientSchema, SignUpSchema, \
    LoginAuthenSchema, SessionSchema, ReqTag, RepTag
from utils import hashmap, getFriends, writeToStorage
from Synchronization import ReadWriteLock

lock = ReadWriteLock()
clients = {} # an ID can have multiple instances, e.g 1 : [conn1, conn2]
sessions = [] # online users

# broadcast status of a friend
def updateStatus(id, type=RepTag.ONLINE):
    lock.acquire_read()
    with open('Users.json', 'r') as openfile:
        users = json.load(openfile)
    lock.release_read()
    for friend in users[id]['friends']:
        if friend in clients:
            for conn in clients[friend]:
                conn.send(json.dumps({'type': type,
                                      'friend': id}))

# create session
def createSession(addr,srcID,destID):
    if destID not in clients: # user not online
        raise Exception('friend not online')
    # add session if not exist
    if (srcID,destID) not in sessions and \
       (destID,srcID) not in sessions:
        sessions.append((srcID,destID))
    for conn in clients[destID]:
        conn.send(json.dumps({
            'type': ReqTag.SESSION_OPEN,
            'id': srcID,
            'ip': addr[0],
            'port': addr[1]
        }))

# peer handling function
def peerConnection(conn,addr):
    try:
        data = json.loads(conn.recv(1024))
        client = ClientSchema().load(data)
        # connection set
        if client['type'] == ReqTag.LOGIN:
            # login authentication
            LoginAuthenSchema().load(data)
            friendlist = getFriends(client['username'], clients)
            conn.send(json.dumps({'type': RepTag.LOGIN_SUCCESS,
                                  'friendlist':friendlist})) # send back friendlist
        else: # sign up validation
            SignUpSchema().load(data)
            # add to hashmap
            hashmap[client['username']] = len(hashmap)
            # add to Users.json
            writeToStorage({
                'nickname': client['nickname'],
                'username': client['username'],
                'password': client['password']
            },lock)
            msg = {'type': RepTag.SIGNUP_SUCCESS,
                   'friendlist':[]}
            conn.send(json.dumps(msg)) # notify success

        # add id to client list; can log in multiple instances simultaneously
        id = hashmap[client['username']]
        clients[id].append(conn)

        # broadcast online status to online friends
        updateStatus(id)

    except Exception as e:
        conn.send(json.dumps({"type": "ERROR",
                              "message": {e.message}}))
        print('Connection closed with :', addr[0], ':', addr[1])
        conn.close()
        return

    # wait for session or disconnect
    while True:
        try:
            data = json.loads(conn.recv(1024))
            req = RequestSchema().load(data)
            if req['type'] == ReqTag.SESSION_OPEN:
                destID = SessionSchema().load(data)['destID']
                createSession(addr,id,destID)
            elif req['type'] == ReqTag.SESSION_REJECT:

            elif req['type'] == ReqTag.SESSION_ACCEPT:

            elif req['type'] == ReqTag.LOGOUT:

        except Exception as e:

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

        print('Connected to :', addr[0], ':', addr[1])

        # Start a new thread and return its identifier
        Thread(target=peerConnection, args=(conn, addr))
    # server.close()