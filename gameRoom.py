GAMES = ["pac-man", "mario"]
import errorDefinitions
import socket
from gameServer import Client
import select

class Game:
    MAX_PLAYERS = 4

    def __init__(self):
        pass

    def handle_response(self, response):
        print("super response")
        return "game_state"


class GameRoom:
    def __init__(self, game, name, game_server):
        self.game = game
        self.game_name = name
        self.max_players = game.MAX_PLAYERS
        self.curr_players = 0
        self.active = 1
        self.game_server = game_server

        self.players = {}
        self.inputs = []
        self.outputs =[]

    def spots_available(self):
        return self.max_players - self.curr_players

    def __repr__(self):
        return f"Game: {self.game_name} Active players: {self.curr_players}"

    def add_player(self, player:Client, s:socket.socket):
        self.players[s] = player
        self.inputs.append(s)

    def delete_player(self,s):
        self.inputs.remove(s)
        if(s in self.outputs):
            self.outputs.remove(s)
        del self.players[s]
        self.game_server.untransfer_client(s)

    def start(self):
        while self.active:
            if self.inputs:
                readable, writable, exceptions = select.select(self.inputs, self.outputs, self.inputs)
                for s in readable:
                    try:
                        response = s.recv(1024)
                    except ConnectionResetError:
                        exceptions.append(s)
                        continue
                    if response:
                        decoded_response = response.decode()
                        if decoded_response == "exit":
                            self.delete_player(s)
                        else:
                            print(f"New response: {decoded_response} from client {self.players[s].name} in GameRoom")

                for s in exceptions:
                    self.inputs.remove(s)
                    if s in self.outputs:
                        self.outputs.remove(s)
                    del self.players[s]
                    s.close()
                    self.curr_players -= 1
                    print("player disconnected")


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


def create_game_room(name):
    if name not in GAMES:
        raise errorDefinitions.InvalidGameName

    return GameRoom(Game(), name)
