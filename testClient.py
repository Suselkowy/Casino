from _thread import *
import socket

HOST = "127.0.0.1"  # The server's hostname or IP address
PORT = 65432  # The port used by the server

id = -1
running = 1
in_game = 0

def sender():
    global running
    while running:
        tmp = input()
        if tmp.split(" ")[0] == "exit":
            running = 0
        s.send(bytes(tmp, 'utf-8'))


def receiver():
    global running
    while running:
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
