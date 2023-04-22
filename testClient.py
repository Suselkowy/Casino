from _thread import *
import socket


HOST = "127.0.0.1"  # The server's hostname or IP address
PORT = 65432  # The port used by the server

id = -1

def sender():
    while 1:
        tmp = input()
        s.send(bytes(tmp, 'utf-8'))


def receiver():
    while 1:
        data = s.recv(1024)
        decoded = data.decode()
        if data is not None:
            print(f"{decoded}")


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    name = input("Tell us your name: ")
    s.connect((HOST, PORT))
    s.send(bytes(name, "utf-8"))
    start_new_thread(receiver, ())
    sender()

