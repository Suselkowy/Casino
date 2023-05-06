import pickle
from enum import Enum

class SendDataType(Enum):
    STRING = 0
    PICKLE = 1

def send_data(data, conn ,type):
    if type == SendDataType.STRING:
        conn.send(b"type string")
        conn.send(data)
    elif type == SendDataType.PICKLE:
        conn.send(b"type pickle")
        conn.sendall(pickle.dump(data))

def receive_data(conn):
    data = conn.recv(11)
    decoded = data.decode()
    if decoded[1] == "string":
        return (SendDataType.STRING, conn.recv(1024))
    else:
        return (SendDataType.PICKLE, pickle.loads(conn.recv(2048 * 2)))


