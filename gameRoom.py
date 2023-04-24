GAMES = ["pac-man", "baccarat", "roulette"]
import errorDefinitions
import socket
from gameServer import Client
import select
import queue
from enum import Enum
from helpers import send_data

from games.baccarat import Baccarat
from games.gameClass import Game
from games.roulette import Roulette

class GameStatus(Enum):
    STOPPED = 0
    NO_CHANGE = 1
    UPDATE = 2


class GameRoom:
    def __init__(self, game, name, game_server):
        self.game = game
        self.game_name = name
        self.max_players = game.MAX_PLAYERS
        self.min_players = game.MIN_PLAYERS
        self.curr_players = 0
        self.active = 1
        self.game_server = game_server
        self.game_status = GameStatus.STOPPED

        self.players = {}
        self.message_queues = {}
        self.inputs = []
        self.outputs = []

        self.game.message_queues = self.message_queues
        self.game.output = self.outputs

    def spots_available(self):
        return self.max_players - self.curr_players

    def __repr__(self):
        return f"Game: {self.game_name} Active players: {self.curr_players}"

    def add_player(self, player: Client, s: socket.socket):
        self.players[s] = player
        self.inputs.append(s)
        self.message_queues[player.conn] = queue.Queue()
        self.game.add_player(player)
        self.curr_players += 1


    def delete_player(self, s):
        if s in self.inputs:
            self.inputs.remove(s)
        if s in self.outputs:
            self.outputs.remove(s)
        del self.players[s]
        self.curr_players -= 1

        if self.curr_players < self.min_players:
            self.game_status = self.game.on_low_players_num()
            # TODO give back players they money

    def untransfer_player(self, s):
        self.delete_player(s)
        self.game_server.untransfer_client(s)

    def disconnect_player(self, s):
        self.delete_player(s)
        self.game_server.disconnect_client(s)

    def start(self):
        while self.active:
            if self.inputs:
                readable, writable, exceptions = select.select(self.inputs, self.outputs, self.inputs, 1)
                for s in readable:
                    try:
                        response = s.recv(1024)
                    except ConnectionResetError:
                        exceptions.append(s)
                        continue

                    if response:
                        decoded_response = response.decode()
                        if decoded_response == "back":
                            self.untransfer_player(s)
                        else:
                            self.game.handle_response(decoded_response, s)

                for s in writable:
                    try:
                        next_msg = self.message_queues[s].get_nowait()
                    except queue.Empty:
                        self.outputs.remove(s)
                    else:
                        send_data(next_msg[0], s, next_msg[1])

                for s in exceptions:
                    self.disconnect_player(s)

                if self.game_status == GameStatus.STOPPED and self.curr_players >= self.min_players:
                    print("Start")
                    self.game_status = GameStatus.UPDATE
                    self.game.status = GameStatus.UPDATE
                    self.game.start()


def search_game_room(game_rooms: [GameRoom], name: str):
    found_rooms_iterator = filter(create_game_room_filter(name), game_rooms)
    list_of_rooms = list(found_rooms_iterator)
    if not len(list_of_rooms):
        return None
    list_of_rooms.sort(key=lambda room: room.curr_players, reverse=True)
    return list_of_rooms


def create_game_room_filter(name):
    def game_room_filter(game_room: GameRoom) -> bool:
        return game_room.spots_available() and game_room.game_name == name

    return game_room_filter


def create_game_room(name, game_server):
    if name not in GAMES:
        raise errorDefinitions.InvalidGameName
    game = None
    if name == "baccarat":
        game = Baccarat()
    elif name == "roulette":
        game = Roulette()
    else:
        game = Game()
    print("new room created")
    return GameRoom(game, name, game_server)
