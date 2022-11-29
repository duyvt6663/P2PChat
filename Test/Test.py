import socket
import pickle
port = 12345
host = 'localhost'
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((host,port))
msg = {
    'type': 'SIN',
    'nickname': 'Dumamay',
    'username': 'KinkSplaser69',
    'password': 'nunezYolokSi2'
}
client.send(pickle.dumps(msg))
data = client.recv(1024)
print(pickle.loads(data))
