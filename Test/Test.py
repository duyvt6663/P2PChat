import socket
import json
import time
port = 12345
host = 'localhost'
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((host,port))
msg = {
    'type': 'LIN',
    'username': 'ChinsuFood0',
    'password': 'VlovvvKoha0920'
}
client.send(json.dumps(msg).encode('utf-8'))
data = client.recv(1024)
print(json.loads(data.decode('utf-8')))
time.sleep(5)
client.send(json.dumps(msg).encode('utf-8'))