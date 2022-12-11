# import socket programming library
import json, pickle
import socket
# import thread module
from _thread import *
import threading
from threading import Thread
# import serializer
from Deserializer import *
from utils import getFriends, writeToStorage
from Synchronization import ReadWriteLock

###################################################################
### Global asset, including lock, online users, and sessions
lock = ReadWriteLock()
clients = {} # online users, an ID can have multiple connection instances, e.g {1 : {conn1 : 'ONL', conn2: 'OFF'} }
sessions = {} # current online chats
with open('HMap.json', 'r') as file:
    hashmap = json.load(file)
###################################################################

# broadcast status of a friend
def updateStatus(id, conn, type=RepTag.ONLINE):
    lock.acquire_read()
    with open('Users.json', 'r') as openfile:
        users = json.load(openfile)
    lock.release_read()
    for friend in users[id]['friends']:
        if friend in clients:  # friend has connection to server
            # broadcast to all online instance of friend
            for con in clients[friend]:  # all instances of a friend
                if clients[friend][con] == 'ONLINE':
                    con.sendall(json.dumps({
                        'type': type,
                        'friend': id
                    }).encode('utf-8'))
    clients[id][conn] = 'ONLINE' if type == RepTag.ONLINE else 'OFFLINE'
# broadcast status of a session
def updateSession(srcID, destID,tag='COMPLETELY', type = ReqTag.SESSION_CLOSE):
    if srcID in clients:
        for conn in clients[srcID]:
            if clients[srcID][conn] == 'ONLINE':
                conn.sendall(json.dumps({
                    'type': type,
                    'with': destID,
                    'status': tag
                }).encode('utf-8'))
    if destID in clients:
        for conn in clients[destID]:
            if clients[destID][conn] == 'ONLINE':
                conn.sendall(json.dumps({
                    'type': type,
                    'with': srcID,
                    'status': tag
                }).encode('utf-8'))

# create session
def createSession(addr,srcID,destID,tag=ReqTag.SESSION_OPEN):
    if destID not in clients: # user not online
        raise Exception('friend not online')
    # add session if not exist
    if (srcID,destID) not in sessions and \
       (destID,srcID) not in sessions:
        sessions[(srcID,destID)] = 0 # set new session
    # increment the current session seed
    incrementSession(srcID,destID)
    # session already exists
    for conn in clients[destID]:
        if clients[destID][conn] == 'ONLINE':
            conn.sendall(json.dumps({
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
    if unit < 0:
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
        'password': client['password'],
        'friends': []
    }, lock)
    msg = {'type': RepTag.SIGNUP_SUCCESS,
           'id': hashmap[client['username']],
           'friendlist': []}
    conn.sendall(json.dumps(msg).encode('utf-8'))  # notify success

# post signup/login update
def updateUser(conn, id):
    # add id to client list; can log in multiple instances simultaneously
    if id not in clients:
        clients[id] = {}
    clients[id][conn] = 'ONLINE'
    # broadcast online status to online friends
    updateStatus(id, conn)

# disconnect util function
def disconnect(conn, id):
    # exception-free section -> no send
    if id == -1:  # no login, signup etc.
        return
    # id valid
    # update status
    updateStatus(id, conn, RepTag.OFFLINE)
    clients[id].pop(conn)
    if not clients[id]:
        clients.pop(id)
        # close related sessions when no connection from the same id found
        for i in range(len(hashmap)):
            incrementSession(id, i, -1)


# peer handling function
def peerConnection(conn, addr):
    # state handling
    id = -1 # default id
    while True:
        try:
            data = conn.recv(1024)
            data = json.loads(data.decode('utf-8'))
        except ConnectionResetError:
            disconnect(conn, id)
            print(f'Disconnected to: ', addr[0], ':', str(addr[1]))
            return
        try:
            # always authenticate by login or sign up first due to no session token
            if data['type'] == ReqTag.LOGIN:
                # login authentication
                lock.acquire_read()
                LoginAuthenSchema().load(data)
                lock.release_read()
                friendlist = getFriends(data['username'], clients, lock)
                id = hashmap[data['username']]
                lock.acquire_read()
                with open('Users.json', 'r') as file:
                    users = json.load(file)  # read nickname in
                lock.release_read()

                conn.send(json.dumps({
                    'type': RepTag.LOGIN_SUCCESS,
                    'id': id,
                    'nickname': users[id]['nickname'],
                    'friendlist': friendlist
                }).encode('utf-8'))  # send back friendlist

                updateUser(conn, id)
            elif data['type'] == ReqTag.SIGNUP:
                lock.acquire_read()
                SignUpSchema().load(data)
                lock.release_read()
                signup(conn, data)
                id = hashmap[data['username']]
                updateUser(conn, id)

            elif data['type'] == ReqTag.SESSION_OPEN:
                SessionSchema().load(data)
                createSession((data['ip'], data['port']), id, data['destID'])

            elif data['type'] == ReqTag.SESSION_REJECT:
                destID = BriefSessionSchema().load(data)['destID']
                conn.send(json.dumps(data).encode('utf-8'))
                updateSession(id, destID)
                # pop session
                sessions.pop((destID, id))
                sessions.pop((id, destID))

            elif data['type'] == ReqTag.SESSION_ACCEPT:
                SessionSchema().load(data)
                createSession((data['ip'], data['port']), id, data['destID'],
                              ReqTag.SESSION_ACCEPT)

            elif data['type'] == ReqTag.SESSION_CLOSE:
                destID = SessionSchema().load(data)['destID']
                incrementSession(id, destID, -1)

            elif data['type'] == ReqTag.LOGOUT: # logout, update status
                updateStatus(id, conn, RepTag.OFFLINE)
                id = -1

            else:  # disconnect or gibberish data
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
            except:
                continue
    # connection closed
    # conn.close()


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