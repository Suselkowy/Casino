import socket
import select
import queue
from clientClass import Client
from databaseClass import Database
from errorDefinitions import *
import gameRoom
from _thread import *

class Server:
    def __init__(self, MAX_USERS_CONNECTED, SERVER_IP, SERVER_PORT):
        self.MAX_USERS_CONNECTED = MAX_USERS_CONNECTED
        self.SERVER_IP = SERVER_IP
        self.SERVER_PORT = SERVER_PORT
        self.num_of_connected_clients = 0
        self.database = Database()

        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.init_socket()

        self.connected_clients = {}

        self.inputs = [self.s]
        self.outputs = []
        self.message_queues = {self.s: queue.Queue()}
        self.game_rooms:[gameRoom.GameRoom] = []
        self.add_data()

    def add_data(self):
        taken = [1,2,3,4]
        names = ["pac-man", "pac-man", "roc-man", "pac-man"]
        for num, name in zip(taken, names):
            tmp = gameRoom.GameRoom(gameRoom.Game(), name, self)
            tmp.curr_players = num
            self.game_rooms.append(tmp)
        for room in self.game_rooms:
            start_new_thread(self.start_room, (room,))

    def init_socket(self):
        self.s.bind((self.SERVER_IP, self.SERVER_PORT))
        self.s.setblocking(0)
        self.s.listen(self.MAX_USERS_CONNECTED)

    def generate_client(self, response: str, conn: socket.socket(), addr):
        balance = self.database.get_balance_by_name(response)
        if not balance:
            balance = self.database.create_client(response)

        return Client(conn, addr, response, balance)

    def start(self):
        while self.inputs:
            readable, writable, exceptions = select.select(self.inputs, self.outputs, self.inputs)

            for s in readable:
                if s == self.s:
                    conn, addr = self.s.accept()
                    default_timeout = conn.gettimeout()
                    conn.settimeout(5)
                    try:
                        identification_response = conn.recv(1024)
                        if not identification_response: raise InvalidResponseException
                        decoded_response = identification_response.decode()

                        new_client = self.generate_client(decoded_response, conn, addr)
                        self.connected_clients[conn] = new_client
                        self.message_queues[conn] = queue.Queue()
                        self.inputs.append(conn)
                    except socket.timeout:
                        conn.close()
                        continue
                    except InvalidResponseException:
                        conn.close()
                        continue

                    conn.settimeout(default_timeout)
                    conn.setblocking(0)
                    self.num_of_connected_clients += 1
                    print("Player connected")
                else:
                    try:
                        response = s.recv(1024)
                    except ConnectionResetError:
                        exceptions.append(s)
                        continue
                    if response:
                        decoded_response = response.decode()
                        try:
                            self.handle_client_response(decoded_response, s)

                            #print(f"New response: {decoded_response} from client {self.connected_clients[s].name}")
                        except InvalidResponseException:
                            print("Invalid response")
                        except InvalidUserException:
                            print("Invalid user id")

            for s in writable:
                try:
                    next_msg = self.message_queues[s].get_nowait()
                except queue.Empty:
                    pass
                else:
                    s.send(next_msg)

            for s in exceptions:
                self.inputs.remove(s)
                if s in self.outputs:
                    self.outputs.remove(s)
                del self.connected_clients[s]
                del self.message_queues[s]
                s.close()
                self.num_of_connected_clients -= 1
                print("player disconnected")

    def transfer_client(self, game_room, s):
        self.inputs.remove(s)
        if s in self.outputs:
            self.outputs.remove(s)
        game_room.add_player(self.connected_clients[s], s)
        print("transfered player")

    def untransfer_client(self, s):
        self.inputs.append(s)
        print("untransfered player")

    def handle_client_response(self, response, s):
        try:
            split_response = response.split(":")
            name = split_response[0]
            data = split_response[1:]

        except IndexError:
            raise InvalidResponseException

        if not self.database.get_balance_by_name(name):
            raise InvalidUserException

        try:
            if data[0] == "play":
                found_rooms = gameRoom.search_game_room(self.game_rooms, data[1])
                if len(found_rooms) == 0:
                    new_room = gameRoom.create_game_room(name)
                    self.game_rooms.append(new_room)
                    found_rooms.append(new_room)
                self.transfer_client(found_rooms[0], s)

            else:
                raise InvalidResponseException

        except IndexError:
            raise InvalidResponseException
        except InvalidResponseException:
            raise InvalidResponseException
        except InvalidGameName:
            raise InvalidResponseException

        return 0

    def start_room(self, game_room):
        game_room.start()

if __name__ == "__main__":
    server = Server(4, "127.0.0.1", 65432)
    server.start()
