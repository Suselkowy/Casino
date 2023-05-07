from kivy.app import App
from kivy.uix.label import Label
from kivy.lang import Builder
from kivy.properties import ObjectProperty
from kivy.uix.screenmanager import ScreenManager, Screen
from _thread import *
import socket
from helpers import receive_data, SendDataType
import threading

HOST = "127.0.0.1"  # The server's hostname or IP address
PORT = 65432  # The port used by the server

id = -1
running = 1
in_game = 0

curr_screen_handle_function = None

kv = Builder.load_file("my.kv")
sm = ScreenManager()


def send_message(message):
    s.send(bytes(message, 'utf-8'))


# Declare both screens
class LoginScreen(Screen):
    login_input = ObjectProperty(None)

    def btn(self):
        if self.ids.login_input.text:
            s.connect((HOST, PORT))
            s.send(bytes(self.ids.login_input.text, "utf-8"))
            sm.current = 'second'
            start_new_thread(receiver, ())


class SecondScreen(Screen):
    def change_game(self, name):
        send_message(f"play {name}")
        sm.current = 'game'


class GameScreen(Screen):

    def add_message(self):
        tmp = Label(text="Name: ")
        self.ids.message_holder.add_widget(tmp)

    def btn(self):
        if self.ids.message_input.text is not None:
            send_message(self.ids.message_input.text)

    def handle_message(self, message):
        if message is not None:
            if message[0] == SendDataType.STRING:
                self.add_message()
                print(f"{message [1].decode()}")
            else:
                print(f"{message [1]}")


class TestApp(App):
    def build(self):
        # Create the screen manager
        root = sm
        sm.add_widget(LoginScreen(name='login'))
        sm.add_widget(SecondScreen(name='second'))
        sm.add_widget(GameScreen(name='game'))

        sm.current = 'login'


        return sm



# def sender():
#     global running
#     while running:
#         tmp = input()
#         if tmp.split(" ")[0] == "exit":
#             running = 0
#         s.send(bytes(tmp, 'utf-8'))


def receiver():
    global running
    while running:
        data = receive_data(s)
        sm.current_screen.handle_message(data)
        if data is not None:
            print(f"{data[1].decode()}")


if __name__ == '__main__':
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    TestApp().run()
