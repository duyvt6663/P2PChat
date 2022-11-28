import json
hashmap = {
    "KinkSplaster69": 0,
    "LobsterChan323": 1
}

#def updateHashMap(username):

def getFriends(username, clients):
    id = hashmap[username]
    with open('Users.json', 'r') as openfile:
        users = json.load(openfile)
    res = []
    for i in users[id]['friends']:
        res.append({'id': i,
                    'nickname': users[i]['nickname'],
                    'status': hashmap[username] in clients})
    return res
