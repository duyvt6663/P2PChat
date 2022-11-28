# import socket programming library
import socket

# import thread module
from _thread import *
import threading
from threading import Thread

print_lock = threading.Lock()


# peer handling function
def peerConnection(conn):
    data = conn.recv(1024)
    serialize(data)
    while True:

        # data received from client
        data = conn.recv(1024)
        if not data:
            print('Bye')

            # lock released on exit
            print_lock.release()
            break

        # reverse the given string from client
        data = data[::-1]

        # send back reversed string to client
        conn.send(data)

    # connection closed
    conn.close()


def Main():
    host = ""

    # reserve a port on your computer
    # in our case it is 12345 but it
    # can be anything
    port = 12345
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
        Thread(target=peerConnection, args=(conn,))
    #server.close()


if __name__ == '__main__':
    Main()