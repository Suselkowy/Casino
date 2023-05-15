import random

from games.gameClass import Game, GameStatus
from helpers import SendDataType
import time
from errorDefinitions import InvalidBet
from _thread import *


class Roulette(Game):
    MAX_PLAYERS = 100
    MIN_PLAYERS = 1

    def __init__(self):
        super().__init__()
        self.bets = dict()
        self.isBetTime = 0
        self.state = 0
        random.seed(time.time())

    def roll(self):
        return random.randint(0, 36)

    def handle_response(self, response, s):
        super(Roulette, self).handle_response(response, s)
        if self.status != GameStatus.STOPPED:
            if response == "commands":
                self.message_queues[s].put((bytes("""Available commands:
    -Betting:
        bet [red|black] <amount>
    -Quit
        back""", "utf-8"), SendDataType.STRING))
                self.output.append(s)
            elif not self.isBetTime:
                self.message_queues[s].put((b"Cant place bets now, wait", SendDataType.STRING))
                self.output.append(s)
            else:
                try:
                    info = response.split(" ")
                    if self.bets.get(s) is None:
                        self.bets[s] = {"green": 0, "red": 0, "black": 0}

                    amount = int(info[2])

                    if self.players[s].balance < amount:
                        raise InvalidBet

                    self.players[s].balance -= amount
                    self.bets[s][info[1]] += amount

                    self.message_queues[s].put((b"Bet placed", SendDataType.STRING))
                    self.output.append(s)
                except Exception as e:
                    self.message_queues[s].put((b"Invalid bet", SendDataType.STRING))
                    self.output.append(s)

    def calculate_winning(self, p_dict, rolled):
        if rolled % 2 == 0:
            return p_dict['red'] * 2
        if rolled == 0:
            return p_dict['green'] * 14

        return p_dict['black'] * 2

    def start(self):
        pass

    def handle_timer(self):
        if self.state == 0:
            if time.time() - self.time_of_last_move >= 10:
                self.isBetTime = 0

                for client_key in self.players.keys():
                    self.output.append(client_key)
                    self.message_queues[client_key].put((b"Rolling...", SendDataType.STRING))
                self.state = 1
                self.status = GameStatus.UPDATE
                self.time_of_last_move = time.time()
        elif self.state == 1:
            if time.time() - self.time_of_last_move >= 0.7:
                rolled = self.roll()
                for client_key in self.players.keys():
                    self.output.append(client_key)
                    self.message_queues[client_key].put((bytes(
                        f"Number rolled: {rolled} - {'black' if rolled % 2 == 1 else ('red' if rolled != 0 else 'green')}",
                        "utf-8"), SendDataType.STRING))

                for client_key in self.players.keys():
                    if self.bets.get(client_key) is not None:
                        client_score = self.calculate_winning(self.bets[client_key], rolled)
                        self.players[client_key].balance += client_score

                        message = f"You won: {client_score}"

                        if client_score == 0:
                            message = "You lost"

                        self.output.append(client_key)
                        self.message_queues[client_key].put(
                            (bytes(message, "utf-8"), SendDataType.STRING))

                self.bets.clear()
                self.state = 2
                self.status = GameStatus.UPDATE
                self.time_of_last_move = time.time()
        elif self.state == 2:
            if time.time() - self.time_of_last_move >= 4:
                for client_key in self.players.keys():
                    self.output.append(client_key)
                    self.message_queues[client_key].put((b"Its betting time", SendDataType.STRING))

                self.isBetTime = 1
                self.state = 0
                self.status = GameStatus.UPDATE
                self.time_of_last_move = time.time()
