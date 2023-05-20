import sqlite3
import os

DB_NAME = 'casino_database.db'

check_file = os.path.isfile('./' + DB_NAME)

conn = sqlite3.connect('casino_database.db')

if not check_file:
    conn.execute('''CREATE TABLE Clients
                 (ClientID INT PRIMARY KEY     NOT NULL,
                 ClientName     varchar(50) UNIQUE   NOT NULL,
                 Balance          INT     NOT NULL);''')

    conn.execute('''CREATE TABLE Game
    (
    GameID INT PRIMARY KEY     NOT NULL,
    GameName varchar(50)       NOT NULL
    )
    ''')

    conn.execute('''CREATE TABLE GamesHistory
                 (GamesHistoryID INT PRIMARY KEY   NOT NULL,
                 GameID INT                 NOT NULL,
                 ClientID INT               NOT NULL,
                 DatePlayed date            NOT NULL,
                 Win bit                    NOT NULL,
                 Earnings INT               NOT NULL,
                 Loss INT                   NOT NULL
                 );''')


def insert_client(client_name, balance):
    cursor = conn.execute("SELECT MAX(ClientID) FROM Clients")
    try:
        for row in cursor:
            client_id = int(row[0]) + 1
    except TypeError:
        client_id = 0

    conn.execute("INSERT INTO Clients (ClientID, ClientName, Balance) \
              VALUES (?, ?, ?)", (client_id, client_name, balance))
    conn.commit()


def insert_game_history(client_name, game_name, win, earnings, loss):
    cursor = conn.execute("SELECT ClientID FROM Clients WHERE ClientName = ?", client_name)
    for row in cursor:
        client_id = row[0]

    cursor = conn.execute("SELECT GameID FROM Games WHERE GameName = ?", game_name)
    for row in cursor:
        game_id = row[0]

    cursor = conn.execute("SELECT MAX(GamesHistoryID) FROM GamesHistory")
    try:
        for row in cursor:
            games_history_id = int(row[0]) + 1
    except TypeError:
        games_history_id = 0

    conn.execute("INSERT INTO GamesHistory (GamesHistoryID, GameID, ClientID, DatePlayed, Win, Earnings, Loss) \
          VALUES (?, ?, ?, date(), ?, ?, ?)", (games_history_id, game_id, client_id, win, earnings, loss))
    conn.commit()


def change_balance(client_name, amount):  # amount should be positive if add, negative if subtract
    cursor = conn.execute("SELECT ClientID FROM Clients WHERE ClientName = ?", client_name)
    for row in cursor:
        client_id = row[0]
    cursor = conn.execute("SELECT Balance FROM Clients WHERE ClientID = ?", client_id)
    for row in cursor:
        balance = row[0]
    balance += amount

    conn.execute("UPDATE Clients set Balance = ? where ClientID = ?", (balance, client_id))
    conn.commit()
