import pickle
from enum import Enum

class SendDataType(Enum):
    STRING = 0
    PICKLE = 1

def send_data(data, conn ,type):
    if type == SendDataType.STRING:
        msg_len = len(data)
        header_2 = msg_len.to_bytes(4, byteorder='big')
        conn.send(b"type string " + header_2)
        conn.send(data)
    elif type == SendDataType.PICKLE:
        conn.send(b"type pickle ")
        conn.sendall(pickle.dump(data))

def receive_data(conn):
    data = conn.recv(16)
    msg_len = int.from_bytes(data[12:16], byteorder="big")
    decoded = data[:11].decode()
    if decoded[1] == "string":
        return (SendDataType.STRING, conn.recv(1024))
    else:
        return (SendDataType.PICKLE, pickle.loads(conn.recv(2048 * 2)))


