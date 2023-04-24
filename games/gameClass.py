from enum import Enum
import socket
from gameServer import Client
from helpers import SendDataType

class GameStatus(Enum):
    STOPPED = 0
    NO_CHANGE = 1
    UPDATE = 2

class Game:
    MAX_PLAYERS = 1
    MIN_PLAYERS = 1

    def __init__(self):
        self.message_queues: {socket.socket: (any, SendDataType)} = {}
        self.output = []
        self.players: {socket.socket: Client} = {}
        self.status = GameStatus.STOPPED

    def handle_response(self, response, s):
        if self.status == GameStatus.STOPPED:
            self.players[s].balance += 100
            self.message_queues[s].put(
                (bytes(f"waiting pr players", "utf-8"), SendDataType.STRING))
            self.output.append(s)


    def add_player(self, player):
        self.players[player.conn] = player

    def del_player(self, player):
        del self.players[player.conn]

    def start(self):
        pass