import random
from enum import Enum
from helpers import SendDataType
from errorDefinitions import InvalidResponseException
import socket
from clientClass import Client
import time
from games.gameClass import Game, GameStatus

FIGURES = ["J", "Q", "K"]

class Outcome(Enum):
    tie = 0
    player = 1
    banker = 2
    nobody = -1

    def next(self):
        return Outcome((self.value+1)%3)


def valueToFigure(value):
    if value == 1:
        return "A"
    elif value <= 10:
        return str(value)
    else:
        return FIGURES[value - 11]


class Baccarat(Game):
    MAX_PLAYERS = 1
    MIN_PLAYERS = 1

    def __init__(self):
        super().__init__()
        self.bets = {"tie": 0, "player": 0, "banker": 0}
        self.cards = Deck()
        self.table = [[], []]
        self.player = None

    def handle_response(self, response, s):
        super(Baccarat, self).handle_response(response, s)
        if self.status != GameStatus.STOPPED:
            split_response = response.split(" ")
            if not split_response:
                raise InvalidResponseException

            betNr = self.betsParser(response)

            sums = [0, 0]
            if betNr == 1:
                outcome = self.FirstRound(sums)

                if outcome.value >= 0:
                    self.handleWin(outcome)
                else:
                    self.displayTable()
                    outcome = self.SecondRound(sums)
                    self.handleWin(outcome)
                self.clear()


    def start(self):
        for key in self.players.keys():
            self.player = key
        self.message_queues[self.player].put((b"Welcome to baccarat!!\n To see all available commands type 'commands'", SendDataType.STRING))
        self.output.append(self.player)


    def handleWin(self, outcome:Outcome):
        if self.bets[outcome.name] == 0:
            self.message_queues[self.player].put((bytes(f"-{self.bets[outcome.next().name] + self.bets[outcome.next().next().name]}","utf-8"), SendDataType.STRING))
            self.output.append(self.player)
        else:
            self.players[self.player].balance += self.bets[outcome.name]*2
            self.message_queues[self.player].put((bytes(f"+{self.bets[outcome.name]}","utf-8"), SendDataType.STRING))
            self.output.append(self.player)

    def FirstRound(self,sums):
        self.table[0].append(self.cards.draw())
        self.table[1].append(self.cards.draw())
        self.table[0].append(self.cards.draw())
        self.table[1].append(self.cards.draw())

        playerSum = (self.table[0][0].value + self.table[0][1].value)%10
        bankerSum = (self.table[1][0].value + self.table[1][1].value)%10

        sums[0] = playerSum
        sums[1] = bankerSum

        self.displayTable()

        if playerSum == bankerSum and playerSum not in (8,9):
            self.message_queues[self.player].put((b"Its a Tie!", SendDataType.STRING))
            self.output.append(self.player)
            return Outcome.tie
        elif playerSum in (8,9):
            self.message_queues[self.player].put((b"Player wins!", SendDataType.STRING))
            self.output.append(self.player)
            return Outcome.player
        elif bankerSum in (8,9):
            self.message_queues[self.player].put((b"Banker wins!", SendDataType.STRING))
            self.output.append(self.player)
            return Outcome.banker
        else:
            return Outcome.nobody

    def SecondRound(self,sums):
        isPlayerPat = 0
        playerThirdCard = 0
        bankerThirdCard = 0

        playerTotal = sums[0]
        bankerTotal = sums[1]

        if playerTotal <= 5:
            isPlayerPat = 1
            newCard = self.cards.draw()
            self.table[0].append(newCard)
            playerThirdCard = newCard.value

        if isPlayerPat:
            if bankerTotal <= 2 or (bankerTotal == 3 and playerThirdCard != 8) or (bankerTotal == 4 and  2 <= playerThirdCard <= 7) or\
            (bankerTotal == 5 and 4 <= playerThirdCard <= 7) or ( bankerTotal == 6 and 6 <= playerThirdCard <= 7):
                newCard = self.cards.draw()
                self.table[0].append(newCard)
                bankerThirdCard = newCard.value


        playerTotal = (playerTotal+playerThirdCard)%10
        bankerTotal = (bankerTotal + bankerThirdCard)%10
        if playerTotal == bankerTotal:
            self.message_queues[self.player].put((b"Its a Tie!", SendDataType.STRING))
            self.output.append(self.player)
            return Outcome.tie
        else:
            if(abs(9 - playerTotal) < abs(9 - bankerTotal)):
                self.message_queues[self.player].put((b"Player wins!", SendDataType.STRING))
                self.output.append(self.player)
                return Outcome.player
            else:
                self.message_queues[self.player].put((b"Banker wins!", SendDataType.STRING))
                self.output.append(self.player)
                return Outcome.banker

    def displayTable(self):
        playerCards = " ".join([str(card) for card in self.table[0]])
        bankerCards = " ".join([str(card) for card in self.table[1]])
        self.message_queues[self.player].put((bytes(f"""Player:     Banker:\n{playerCards.ljust(11)}{bankerCards}\n""", "utf-8"), SendDataType.STRING))
        self.output.append(self.player)

    def betsParser(self, bet):
        try:
            betSplited = bet.split(" ")
            if betSplited[0] == "commands":
                self.message_queues[self.player].put((bytes("""Available commands:
    -Betting:
        bet [tie|banker|player] <amount>
    -Quit
        quit""", "utf-8"), SendDataType.STRING))
                self.output.append(self.player)
                return 0
            elif betSplited[0] == "bet":
                if self.bets.get(betSplited[1]) is not None:
                    amount = int(betSplited[2])
                    if amount < 0:
                        self.message_queues[self.player].put((bytes("Invalid bet", "utf-8"), SendDataType.STRING))
                        self.output.append(self.player)
                        return -1
                    if self.players[self.player].balance < amount:
                        self.message_queues[self.player].put((bytes("Not enough money", "utf-8"), SendDataType.STRING))
                        self.output.append(self.player)
                        return -1
                    self.bets[betSplited[1]] = amount
                    self.players[self.player].balance -= amount
                    return 1
        except:
            pass
        self.message_queues[self.player].put((bytes("Invalid bet", "utf-8"), SendDataType.STRING))
        self.output.append(self.player)
        return -1


    def clear(self):
        self.table = [[], []]
        for key in self.bets:
            self.bets[key] = 0


class Deck:
    def __init__(self):
        self.cards = []
        self.fillDeck()
        random.seed(time.time())

    def fillDeck(self):
        self.cards = []
        for deck in range(6):
            for suit in ["♠", "♥", "♦", "♣"]:
                for value in range(1, 14):
                    self.cards.append(Card(suit, value))
        self.shuffle()

    def shuffle(self):
        random.shuffle(self.cards)

    def draw(self):
        if len(self.cards) <= 7:
            self.fillDeck()

        return self.cards.pop()



class Card:
    def __init__(self, suit, val):
        self._suit = suit
        self._value = val

    def __str__(self):
        return f"{valueToFigure(self._value)}{self._suit}"
    @property
    def value(self):
        return self._value if self._value <= 10 else 0
