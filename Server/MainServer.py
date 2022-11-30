# import socket programming library
import json, pickle
import socket
# import thread module
from _thread import *
import threading
from threading import Thread
# import serializer
from Deserializer import RequestSchema, ClientSchema, SignUpSchema, \
    LoginAuthenSchema, SessionSchema, ReqTag, RepTag
from utils import getFriends, writeToStorage
from Synchronization import ReadWriteLock

###################################################################
### Global asset, including lock, online users, and sessions
lock = ReadWriteLock()
clients = {} # an ID can have multiple instances, e.g 1 : [conn1, conn2]
sessions = {} # online users
with open('HMap.json', 'r') as file:
    hashmap = json.load(file)
###################################################################

# broadcast status of a friend
def updateStatus(id, type=RepTag.ONLINE):
    lock.acquire_read()
    with open('Users.json', 'r') as openfile:
        users = json.load(openfile)
    lock.release_read()
    for friend in users[id]['friends']:
        if friend in clients: # friend is online
            for conn in clients[friend]: # all instances of a friend
                conn.send(json.dumps({'type': type,
                                      'friend': id}).encode('utf-8'))

# broadcast status of a session
def updateSession(srcID, destID, tag='COMPLETELY'):
    lock.acquire_read()
    with open('Users.json', 'r') as file:
        users = json.load(file)
    lock.release_read()
    clients[srcID].send(json.dumps({
        'type': ReqTag.SESSION_CLOSE,
        'with': users[destID]['nickname'],
        'status': tag
    }).encode('utf-8'))
    clients[destID].send(json.dumps({
        'type': ReqTag.SESSION_CLOSE,
        'with': users[srcID]['nickname'],
        'status': tag
    }).encode('utf-8'))

# create session
def createSession(addr,srcID,destID,tag=ReqTag.SESSION_OPEN):
    if destID not in clients: # user not online
        raise Exception('friend not online')
    # add session if not exist
    if (srcID,destID) not in sessions and \
       (destID,srcID) not in sessions:
        sessions[(srcID,destID)] = 1 # one user waiting on session
    # session already exists
    for conn in clients[destID]:
        conn.send(json.dumps({
            'type': tag,
            'id': srcID,
            'ip': addr[0],
            'port': addr[1]
        }).encode('utf-8'))

# add/subtract user from session
def incrementSession(srcID, destID, unit=1):
    if (srcID, destID) in sessions:
        ind = (srcID, destID)
    elif (destID,srcID) in sessions:
        ind = (destID,srcID)
    else:
        return
    sessions[ind] += unit
    if not sessions[ind]:
        # destroy session
        sessions.pop(ind)
        tag = 'COMPLETELY'
    else:
        tag = 'PARTIALLY'
    updateSession(srcID,destID,tag)

# signup util function
def signup(conn, client):
    # add to hashmap
    hashmap[client['username']] = len(hashmap)
    # write hashmap back to file
    lock.acquire_write()
    with open('HMap.json', 'w') as file:
        json.dump(hashmap, file, indent=4)
    lock.release_write()
    # add to Users.json
    writeToStorage({
        'nickname': client['nickname'],
        'username': client['username'],
        'password': client['password']
    }, lock)
    msg = {'type': RepTag.SIGNUP_SUCCESS,
           'friendlist': []}
    conn.send(json.dumps(msg).encode('utf-8'))  # notify success

# post signup/login update
def updateUser(data,id):
    # add id to client list; can log in multiple instances simultaneously
    id = hashmap[data['username']]
    if id not in clients:
        clients[id] = []
    clients[id].append(conn)
    # broadcast online status to online friends
    updateStatus(id)

# disconnect util function
def disconnect(conn, id):
    # exception-free section -> no send
    if id == -1: # no login, signup etc.
        return
    # id valid, close related sessions
    for i in range(len(hashmap)):
        incrementSession(id, i, -1)
    # update status
    clients[id].pop(conn)
    if not len(clients[id]):
        clients.pop(id)
    updateStatus(id, RepTag.OFFLINE)
    # reset connection and id
    id = -1


# peer handling function
def peerConnection(conn,addr):
    # state handling
    id = -1  # default id
    while True:
        try:
            data = conn.recv(1024)
            data = json.loads(data.decode('utf-8'))
        except Exception as e:
            disconnect(conn, id, repr(e))
            print(f'Disconnected to: ',addr[0], ':', str(addr[1]))
            return
        try:
            if data['type'] == ReqTag.LOGIN:
                # login authentication
                lock.acquire_read()
                LoginAuthenSchema().load(data)
                lock.release_read()
                friendlist = getFriends(data['username'], clients, lock)
                conn.send(json.dumps({
                    'type': RepTag.LOGIN_SUCCESS,
                    'friendlist': friendlist
                }).encode('utf-8'))  # send back friendlist
                updateUser(data,id)
            elif data['type'] == ReqTag.SIGNUP:
                lock.acquire_read()
                SignUpSchema().load(data)
                lock.release_read()
                signup(conn, data)
                updateUser(data,id)
            elif data['type'] == ReqTag.SESSION_OPEN:
                destID = SessionSchema().load(data)['destID']
                createSession(addr,id,destID)
            elif data['type'] == ReqTag.SESSION_REJECT:
                destID = SessionSchema().load(data)['destID']
                conn.send(json.dumps(data).encode('utf-8'))
                updateSession(id,destID)
                # pop session
                sessions.pop((destID,id))
                sessions.pop((id,destID))
            elif data['type'] == ReqTag.SESSION_ACCEPT:
                destID = SessionSchema().load(data)['destID']
                createSession(addr, id, destID, ReqTag.SESSION_ACCEPT)
            elif data['type'] == ReqTag.SESSION_CLOSE:
                destID = SessionSchema().load(data)['destID']
                incrementSession(id,destID,-1)
            elif data['type'] == ReqTag.LOGOUT: # logout, update status
                clients[id].pop(conn)
                updateStatus(id,RepTag.OFFLINE)
                id = -1
            else: # disconnect or gibberish data
                # request close all related sessions and update status
                disconnect(conn, id)
                conn.close()
                print(f'Disconnected to: ', addr[0], ':', str(addr[1]))
                return

        except Exception as e:
            try:
                conn.send(json.dumps(
                    {"type": "ERROR",
                    "message": repr(e)}
                ).encode('utf-8'))
            except Exception:
                continue

    # connection closed
    conn.close()


# main server thread
if __name__ == '__main__':
    host = ""
    port = 12345  # reserve a port on your computer
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
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
        t = Thread(target=peerConnection, args=(conn, addr))
        t.start()
        #print('hello')
    # server.close()