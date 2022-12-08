import json
from Synchronization import  ReadWriteLock

#def updateHashMap(username):

def getFriends(username, clients, lock):
    lock.acquire_read()
    with open('HMap.json', 'r') as openfile:
        hashmap = json.load(openfile)
    id = hashmap[username]
    with open('Users.json', 'r') as openfile:
        users = json.load(openfile)
    lock.release_read()
    res = []
    for friendID in users[id]['friends']:
        # check if friend is online
        status = 'OFFLINE'
        if friendID in clients:
            for conn in clients[friendID]:
                if clients[friendID][conn] == 'ONLINE':
                    status = 'ONLINE'
                    break
        res.append({'id': friendID,
                    'nickname': users[friendID]['nickname'],
                    'status': status})
    return res

def writeToStorage(new_data, lock, filename='Users.json'):
    lock.acquire_write()
    with open(filename,'r+') as file:
        # First we load existing data into a dict.
        file_data = json.load(file)
        # Join new_data with file_data inside emp_details
        file_data.append(new_data)
        # Sets file's current position at offset.
        file.seek(0)
        # convert back to json.
        json.dump(file_data, file, indent = 4)
    lock.release_write()