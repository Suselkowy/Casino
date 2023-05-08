import socket
import tkinter as tk
from tkinter import messagebox, scrolledtext, TOP, NW
from helpers import receive_data, SendDataType
import threading
from gameRoom import GAMES
import tkinter.font as font

class BaccaratGamePage(tk.Frame):
    def __init__(self, parent, controller, width, height):
        tk.Frame.__init__(self, parent, width=width, height=height)
        self.controller = controller
        self.s = self.controller.s

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
        self.s.send(bytes(message, 'utf-8'))
        self.message_entry.delete(0, tk.END)

    def back(self):
        self.s.send(bytes("back", 'utf-8'))
        self.controller.show_frame('ChooseGamePage')