import socket
import tkinter as tk
from tkinter import messagebox, scrolledtext, TOP, NW
from helpers import receive_data, SendDataType
import threading
from gameRoom import GAMES
import tkinter.font as font
from DiceGUI import DiceGamePage
from RouletteGUI import RouletteGamePage
from BingoGUI import BingoGamePage
from BlackjackGUI import BlackjackGamePage
from BaccaratGUI import BaccaratGamePage
from PIL import Image, ImageTk

# Set up the socket
HOST = "127.0.0.1"  # The server's hostname or IP address
PORT = 65432  # The port used by the server
running = True

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))


class SampleApp(tk.Tk):

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        # the container is where we'll stack a bunch of frames
        # on top of each other, then the one we want visible
        # will be raised above the others
        self.container = tk.Frame(self)
        self.container.pack(side="top", fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)
        self.resizable(0, 0)
        self.s = s

        self.width, self.height = 500, 500
        self.geometry(f"{self.width}x{self.height}")

        self.frames = {}
        for F in (LoginPage, ChooseGamePage, BaccaratGamePage , DiceGamePage, RouletteGamePage, BingoGamePage, BlackjackGamePage):
            page_name = F.__name__
            frame = F(parent=self.container, controller=self, width=self.winfo_height(), height=self.winfo_height())
            if page_name == "GamePage":
                self.handle_function = self.empty_handler
            self.frames[page_name] = frame
            self.update_idletasks()
            # put all of the pages in the same location;
            # the one on the top of the stacking order
            # will be the one that is visible.
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("LoginPage")

    def show_frame(self, page_name):
        frame = self.frames[page_name]
        self.handle_function = frame.handle_message
        frame.tkraise()

    def empty_handler(self, message):
        pass

    def receive_messages(self):
        print("start reciver")
        global running
        while running:
            try:
                data = receive_data(s)
                if data is not None:
                    print(f"{data[1].decode()}")
                    self.handle_function(data)
            except Exception as e:
                print(e)
                app.destroy()
        print("not running")


class LoginPage(tk.Frame):

    def __init__(self, parent, controller, width, height):
        tk.Frame.__init__(self, parent, width=width, height=height)
        self.controller = controller

        self.login_header = tk.Label(self, text="Enter your username")
        self.login_header.pack(pady=20)
        self.login_input = tk.Entry(self)
        self.login_input.pack(pady=20)
        self.login_button = tk.Button(self, text='Login', command=self.login)
        self.login_button.pack(pady=20)

    def login(self):
        login_value = self.login_input.get()
        print(login_value)
        if login_value is not None:
            s.send(bytes(login_value, "utf-8"))
            receive_thread = threading.Thread(target=self.controller.receive_messages)
            receive_thread.start()
            self.controller.show_frame("ChooseGamePage")

    def handle_message(self, data):
        pass


class ChooseGamePage(tk.Frame):

    def __init__(self, parent, controller, width, height):
        tk.Frame.__init__(self, parent, width=width, height=height)
        buttons = []
        self.controller = controller
        self.parent = parent
        button_w = self.controller.winfo_width() // 3
        button_h = self.controller.winfo_height() // 2

        curr_row = 0
        curr_col = 0
        i = 0

        for game in GAMES:
            buttons.append(tk.Button(self, text=f"{game}", width=17, height=9))
            buttons[i].grid(row=curr_row, column=curr_col, padx=8, pady=8, ipadx=10, ipady=40)
            buttons[i].bind(f"<Button-1>", self.callback)

            i += 1
            curr_col += 1
            if curr_col >= 3:
                curr_col = 0
                curr_row += 1

    def handle_message(self, data):
        pass

    def callback(self, event):
        clicked_btn = event.widget
        self.load_game(clicked_btn['text'])

    def load_game(self, name):
        print(f"play {name}")
        s.send(bytes(f"play {name}", 'utf-8'))
        self.controller.show_frame(name.title() + "GamePage")

if __name__ == "__main__":
    app = SampleApp()
    app.mainloop()
