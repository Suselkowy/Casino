import socket
import tkinter as tk
from tkinter import messagebox, scrolledtext, TOP, NW
from helpers import receive_data, SendDataType
import threading
from gameRoom import GAMES
import tkinter.font as font
from PIL import Image, ImageTk

class RouletteGamePage(tk.Frame):

    def __init__(self, parent, controller, width, height):
        tk.Frame.__init__(self, parent, width=width, height=height)
        self.controller = controller
        self.s = self.controller.s

        self.isBetTime = 0
        self.ft = font.Font(family='Times', size=10)
        self.roulette_fonts = {'red':'black', 'black':'red', 'green':'black'}

        bet_entry = tk.Entry(self)
        bet_entry["borderwidth"] = "1px"
        bet_entry["font"] = self.ft
        bet_entry["fg"] = "#333333"
        bet_entry["justify"] = "center"
        bet_entry["text"] = "Entry"
        self.bet_entry = bet_entry
        self.bet_entry.place(x=170, y=180, width=166, height=30)

        red_btn = tk.Button(self)
        red_btn["bg"] = "#f0f0f0"
        red_btn["font"] = self.ft
        red_btn["fg"] = "#000000"
        red_btn["justify"] = "center"
        red_btn["text"] = "Red"
        red_btn["command"] = lambda: self.bet_handler("red")
        self.red_btn = red_btn
        self.red_btn.place(x=120, y=260, width=70, height=25)


        green_btn = tk.Button(self)
        green_btn["bg"] = "#f0f0f0"
        green_btn["font"] = self.ft
        green_btn["fg"] = "#000000"
        green_btn["justify"] = "center"
        green_btn["text"] = "Green"
        green_btn["command"] = lambda: self.bet_handler("green")
        self.green_btn = green_btn
        self.green_btn.place(x=220, y=260, width=70, height=25)

        black_btn = tk.Button(self)
        black_btn["bg"] = "#f0f0f0"
        black_btn["font"] = self.ft
        black_btn["fg"] = "#000000"
        black_btn["justify"] = "center"
        black_btn["text"] = "Black"
        black_btn["command"] = lambda: self.bet_handler("black")
        self.black_btn = black_btn
        self.black_btn.place(x=320, y=260, width=70, height=25)

        roulette_outcome = tk.Label(self)
        roulette_outcome["font"] = self.ft
        roulette_outcome["fg"] = "#333333"
        roulette_outcome["justify"] = "center"
        roulette_outcome["text"] = ""
        self.roulette_outcome = roulette_outcome
        self.roulette_outcome.place(x=200, y=60, width=100, height=92)

        back_btn = tk.Button(self)
        back_btn["bg"] = "#f0f0f0"
        back_btn["font"] = self.ft
        back_btn["fg"] = "#000000"
        back_btn["justify"] = "center"
        back_btn["text"] = "Back"
        back_btn["command"] = self.back
        self.back_btn = back_btn
        self.back_btn.place(x=20, y=20, width=70, height=25)


        self.messages_output = tk.Listbox(self)
        self.messages_output["borderwidth"] = "1px"
        self.messages_output["font"] = self.ft
        self.messages_output["fg"] = "#333333"
        self.messages_output["justify"] = "center"
        self.messages_output.place(x=70, y=360, width=361, height=66)

    def bet_handler(self, type):
        if self.bet_entry.get() is not None and self.bet_entry.get().isnumeric():
            self.s.send(bytes(f"bet {type} {self.bet_entry.get()}", 'utf-8'))
        self.bet_entry.delete(0, tk.END)

        self.ft = font.Font(family='Times', size=10)

    def handle_message(self, data):
        message_body = data[1].decode()
        message_split = message_body.split(" ")

        if "Number rolled:" in message_body:
            self.roulette_outcome['text'] = message_split[2]
            self.roulette_outcome['bg'] = message_split[4]
            font_color = self.roulette_fonts.get(message_split[4], 'black')
            self.roulette_outcome['fg'] = font_color

        self.messages_output.insert(tk.END, f"{message_body}\n")

    def back(self):
        self.s.send(bytes("back", 'utf-8'))
        self.controller.show_frame('ChooseGamePage')