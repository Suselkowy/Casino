import socket
import tkinter as tk
from tkinter import messagebox, scrolledtext, TOP, NW
from helpers import receive_data, SendDataType
import threading
from gameRoom import GAMES
import tkinter.font as font
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

        self.width, self.height = 500, 500
        self.geometry(f"{self.width}x{self.height}")

        self.frames = {}
        for F in (LoginPage, ChooseGamePage, GamePage, DiceGamePage):
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
                # messagebox.showerror('Error', 'Lost connection to server')
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


class GamePage(tk.Frame):

    def __init__(self, parent, controller, width, height):
        tk.Frame.__init__(self, parent, width=width, height=height)
        self.controller = controller

        self.back_button = tk.Button(self, text="Back", command=self.back)
        self.back_button.pack(side=TOP, anchor=NW, padx=10, pady=10)

        # Set up the message entry and send button
        self.message_entry = tk.Entry(self)
        self.message_entry.pack(side=tk.LEFT, padx=10, pady=10)
        self.send_button = tk.Button(self, text='Send', command=self.send_message)
        self.send_button.pack(side=tk.LEFT, padx=10, pady=10)

        # Set up the message listbox
        self.message_listbox = scrolledtext.ScrolledText(self, height=20)
        self.message_listbox.pack(side=tk.LEFT, padx=10, pady=10)

    def handle_message(self, data):
        self.message_listbox.insert(tk.END, f"{data[1].decode()}\n")

    def send_message(self):
        message = self.message_entry.get()
        s.send(bytes(message, 'utf-8'))
        self.message_entry.delete(0, tk.END)

    def back(self):
        s.send(bytes("back", 'utf-8'))
        self.controller.show_frame('ChooseGamePage')


class DiceGamePage(tk.Frame):

    def __init__(self, parent, controller, width, height):
        tk.Frame.__init__(self, parent, width=width, height=height)
        self.controller = controller

        self.isRollTime = 0
        self.isBetTime = 0
        self.isMeShooter = 0

        self.dice_imgs = self.init_dice_imgs()

        self.ft = font.Font(family='Times', size=10)

        self.back_btn = tk.Button(self)
        self.back_btn["bg"] = "#f0f0f0"
        self.back_btn["font"] = self.ft
        self.back_btn["fg"] = "#000000"
        self.back_btn["justify"] = "center"
        self.back_btn["text"] = "Back"
        self.back_btn.place(x=10, y=10, width=70, height=25)
        self.back_btn["command"] = self.back

        self.dice_1 = tk.Label(self, image=self.dice_imgs[0])
        self.dice_1["font"] = self.ft
        self.dice_1["fg"] = "#333333"
        self.dice_1["justify"] = "center"
        self.dice_1["text"] = "Dice1"
        self.dice_1.place(x=255, y=40, width=130, height=150)

        self.dice_2 = tk.Label(self, image=self.dice_imgs[0])
        self.dice_2["font"] = self.ft
        self.dice_2["fg"] = "#333333"
        self.dice_2["justify"] = "center"
        self.dice_2["text"] = "Dice2"
        self.dice_2.place(x=365, y=40, width=130, height=150)

        self.roll_btn = tk.Button(self)
        self.roll_btn["bg"] = "#f0f0f0"
        self.roll_btn["font"] = self.ft
        self.roll_btn["fg"] = "#000000"
        self.roll_btn["justify"] = "center"
        self.roll_btn["text"] = "Roll"
        self.roll_btn.place(x=340, y=190, width=70, height=25)
        self.roll_btn["command"] = self.roll

        self.bet_entry = tk.Entry(self)
        self.bet_entry["borderwidth"] = "1px"
        self.bet_entry["font"] = self.ft
        self.bet_entry["fg"] = "#333333"
        self.bet_entry["justify"] = "center"
        self.bet_entry["text"] = "Entry"
        self.bet_entry.place(x=40, y=130, width=171, height=30)

        self.bet_label = tk.Label(self)
        self.bet_label["font"] = self.ft
        self.bet_label["fg"] = "#333333"
        self.bet_label["justify"] = "center"
        self.bet_label["text"] = "Enter bet amount"
        self.bet_label.place(x=70, y=80, width=108, height=30)

        self.pass_btn = tk.Button(self)
        self.pass_btn["bg"] = "#f0f0f0"
        self.pass_btn["font"] = self.ft
        self.pass_btn["fg"] = "#000000"
        self.pass_btn["justify"] = "center"
        self.pass_btn["text"] = "pas"
        self.pass_btn.place(x=40, y=190, width=70, height=25)
        self.pass_btn["command"] = self.pass_handler

        self.dpass_btn = tk.Button(self)
        self.dpass_btn["bg"] = "#f0f0f0"
        self.dpass_btn["font"] = self.ft
        self.dpass_btn["fg"] = "#000000"
        self.dpass_btn["justify"] = "center"
        self.dpass_btn["text"] = "dpass"
        self.dpass_btn.place(x=140, y=190, width=70, height=25)
        self.dpass_btn["command"] = self.dpass_handler

        self.messages_label = tk.Label(self)
        self.messages_label["font"] = self.ft
        self.messages_label["fg"] = "#333333"
        self.messages_label["justify"] = "center"
        self.messages_label["text"] = "Messages"
        self.messages_label.place(x=110, y=290, width=278, height=52)

        self.messages_output = tk.Listbox(self)
        self.messages_output["borderwidth"] = "1px"
        self.messages_output["font"] = self.ft
        self.messages_output["fg"] = "#333333"
        self.messages_output["justify"] = "center"
        self.messages_output.place(x=70, y=360, width=361, height=66)

    def init_dice_imgs(self):
        return [ImageTk.PhotoImage(Image.open(f"assets/dice-{i}.png").resize((80, 80))) for i in range(1, 7)]

    def dpass_handler(self):
        if self.bet_entry.get() is not None and self.bet_entry.get().isnumeric() and self.isBetTime:
            s.send(bytes(f"dpass {self.bet_entry.get()}", 'utf-8'))
        self.bet_entry.delete(0, tk.END)

    def pass_handler(self):
        if self.bet_entry.get() is not None and self.bet_entry.get().isnumeric() and self.isBetTime:
            s.send(bytes(f"pass {self.bet_entry.get()}", 'utf-8'))
        self.bet_entry.delete(0, tk.END)

    def roll(self):
        if self.isRollTime:
            self.isRollTime = 0
            self.roll_btn['bg'] = "#f0f0f0"
            s.send(bytes("roll", 'utf-8'))

    def handle_message(self, data):
        message_body = data[1].decode()
        message_split = message_body.split(" ")

        if len(message_split) == 0:
            return
        elif message_body == "Its betting time":
            self.isBetTime = 1
        elif message_body == "You are a shooter":
            self.isMeShooter = 1
        elif message_split[0] == "Disconnected":
            self.controller.show_frame('ChooseGamePage')
        elif message_body == "Bets ended, time for shooter to roll!":
            self.isRollTime = 1
            self.roll_btn['bg'] = 'green'
        elif message_split[0] == "Rolled":
            str_tuple_1 = message_split[1]
            str_tuple_2 = message_split[2]
            self.dice_1['image'] = self.dice_imgs[int(str_tuple_1[1]) - 1]
            self.dice_2['image'] = self.dice_imgs[int(str_tuple_2[0]) - 1]

        if "waiting for next roll!" in message_body:
            self.isRollTime = 1
            self.roll_btn['bg'] = 'green'

        self.messages_output.insert(tk.END, f"{message_body}\n")

    def back(self):
        s.send(bytes("back", 'utf-8'))
        self.controller.show_frame('ChooseGamePage')


if __name__ == "__main__":
    app = SampleApp()
    app.mainloop()
