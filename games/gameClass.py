from enum import Enum
import socket
from gameServer import Client
from helpers import SendDataType
import time


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
        self.input = []
        self.players: {socket.socket: Client} = {}
        self.status = GameStatus.STOPPED
        self.time_of_last_move = time.time()

    def handle_response(self, response, s):
        if self.status == GameStatus.STOPPED:
            self.message_queues[s].put(
                (bytes(f"waiting pr players", "utf-8"), SendDataType.STRING))
            self.output.append(s)

    def handle_timer(self):
        pass

    def add_player(self, player):
        self.players[player.conn] = player

    def del_player(self, player):
        del self.players[player.conn]
        print("klient usunięty, dostępni:", self.players)

    def start(self):
        pass

    def on_low_players_num(self):
        return GameStatus.NO_CHANGE
