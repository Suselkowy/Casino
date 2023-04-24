import random

from games.gameClass import Game, GameStatus
from helpers import SendDataType
import time
from _thread import *

class Roulette(Game):
    MAX_PLAYERS = 100
    MIN_PLAYERS = 1

    def __init__(self):
        super().__init__()
        self.bets = dict()
        self.isBetTime = 0
        random.seed(time.time())

    def roll(self):
        return random.randint(0, 36)

    def handle_response(self, response, s):
        super(Roulette, self).handle_response(response, s)
        if self.status != GameStatus.STOPPED:
            if not self.isBetTime:
                self.message_queues[self.player].put((b"Cant place bets now, wait", SendDataType.STRING))
                self.output.append(self.player)
            else:
                try:
                    info = response.split(" ")
                    if self.bets.get(s) is None:
                        self.bets[s] = {"green": 0, "red": 0, "black": 0}

                    self.bets[s][self.bets[1]] += int(self.bets[2])
                    self.message_queues[self.player].put((b"Bet placed", SendDataType.STRING))
                    self.output.append(self.player)
                except:
                    self.message_queues[self.player].put((b"Invalid bet", SendDataType.STRING))
                    self.output.append(self.player)

    def threded_roulette(self):
        while 1:
            time.sleep(10)
            self.isBetTime = 0

            for client_key in self.players.keys():
                self.output.append(client_key)
                self.message_queues[client_key].put((b"Rolling...", SendDataType.STRING))
            time.sleep(1)

            rolled = self.roll()
            for client_key in self.players.keys():
                self.output.append(client_key)
                self.message_queues[client_key].put((bytes(f"Number rolled:{rolled} - {'red' if rolled % 2 else 'black' if rolled != 0 else 'green'}",
                              "utf-8"), SendDataType.STRING))

            for client_key in self.players.keys():
                if self.bets.get(client_key) is not None:
                    client_score = self.calculate_winning(self.bets[client_key], rolled)
                    self.output.append(client_key)
                    self.message_queues[client_key].put((bytes(f"You won: {client_score}", "utf-8"), SendDataType.STRING))

            self.bets.clear()

            time.sleep(4)

            for client_key in self.players.keys():
                self.output.append(client_key)
                self.message_queues[client_key].put((b"Its betting time", SendDataType.STRING))

            isBetTime = 1

    def calculate_winning(p_dict, rolled):
        if rolled % 2 == 1:
            return p_dict['red'] * 2
        if rolled == 0:
            return p_dict['green'] * 14
        return p_dict['black'] * 2

    def start(self):
        start_new_thread(self.threded_roulette, tuple())
