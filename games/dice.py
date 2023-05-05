import random

from games.gameClass import Game, GameStatus
from helpers import SendDataType
import time
from _thread import *


class InvalidBet(Exception):
    def __init__(self):
        self.message = "Invalid bet"

    def __repr__(self):
        return self.message


class ShooterDpassBet(Exception):
    def __init__(self):
        self.message = "Shooter can't bet for dpass"

    def __repr__(self):
        return self.message


class Dice(Game):
    MAX_PLAYERS = 16
    MIN_PLAYERS = 1

    def __init__(self):
        super().__init__()
        self.bets = dict()
        self.shooter = None
        self.shooterId = -1
        self.isBetTime = 1
        self.isRollTime = 0
        self.state = 0
        self.point = 0
        random.seed(time.time())

    def roll(self):
        return random.randint(1, 6) + random.randint(1, 6)

    def handle_response(self, response, s):
        super(Dice, self).handle_response(response, s)
        if self.status != GameStatus.STOPPED:
            if response == "commands":
                self.message_queues[s].put((bytes("""Available commands:
    -Betting:
        [pass|dpass] <amount>
    -Rolling
        roll
    -Game rules
        gmrules
    -Quit
        back""", "utf-8"), SendDataType.STRING))
                self.output.append(s)
            elif response == "gmrules":
                self.message_queues[s].put((bytes("""
                pass: 
                    during first round: win on 7 or 11 , lose on 2,3 or 12
                    when none of above are outcomes of throws, the number on dices is now a "Point"
                    during second round: win when "Point" is thrown before 7, lose otherwise
                dpass:
                    during first round: win on 2 or 3, draw on 12, lose on 7 or 11
                    when none of above are outcomes of throws, the number on dices is now a "Point"
                    during second round: win when 7 is is thrown before "Point" , lose otherwise
                Shooter (player currently rolling dices can only bet pass)
                """, "utf-8"), SendDataType.STRING))
                self.output.append(s)
            elif not self.isBetTime:
                self.message_queues[s].put((b"Cant place bets now, wait", SendDataType.STRING))
                self.output.append(s)
            elif response == "roll":
                if self.shooter == s and self.isRollTime:
                    self.handle_roll(self.roll())
                    self.isRollTime = 0
                    self.isBetTime = 0
                elif self.shooter != s:
                    self.message_queues[s].put((b"You are not a shooter!", SendDataType.STRING))
                    self.output.append(s)
                else:  # not self.isRollTime
                    self.message_queues[s].put(
                        (b"Wait for players to place their bets before rolling!", SendDataType.STRING))
                    self.output.append(s)
            else:
                try:
                    info = response.split(" ")
                    if self.bets.get(s) is None:
                        self.bets[s] = {"pass": 0, "dpass": 0}
                    if info[0] == "dpass" and self.shooter == 2:
                        raise ShooterDpassBet
                    self.bets[s][info[1]] += int(info[2])
                    self.message_queues[s].put((b"Bet placed", SendDataType.STRING))
                    self.output.append(s)
                except Exception as e:
                    self.message_queues[s].put((bytes(str(e), "utf-8"), SendDataType.STRING))
                    self.output.append(s)

    # def calculate_winning(self, p_dict, rolled):
    #     if rolled % 2 == 1:
    #         return p_dict['red'] * 2
    #     if rolled == 0:
    #         return p_dict['green'] * 14
    #     return p_dict['black'] * 2

    def handle_roll(self, roll):
        if self.state == 1:  #TODO decide what to do based on roll
            pass

    def handle_skip_roll(self, s):
        #TODO disconnect player s, return all money, switch shooter to next
        self.state = 0

    def start(self):
        self.shooter = self.input[0]
        self.shooterId = 0

    def handle_timer(self):
        if self.state == 0:
            if time.time() - self.time_of_last_move >= 10:
                self.isBetTime = 0

                for client_key in self.players.keys():
                    self.output.append(client_key)
                    self.message_queues[client_key].put((b"Bets ended dice are rolling!", SendDataType.STRING))
                self.state = 1
                self.status = GameStatus.UPDATE
                self.time_of_last_move = time.time()
        elif self.state in (1,2):
            if time.time() - self.time_of_last_move >= 10:
                for client_key in self.players.keys():
                    if self.bets.get(client_key) is not None:
                        self.output.append(client_key)
                        self.message_queues[client_key].put(
                            (bytes(f"Shooter disconnected, returning all bets", "utf-8"), SendDataType.STRING))
                self.state = -1
                self.handle_skip_roll()
