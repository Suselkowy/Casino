class Database:
    START_BALANCE = 100

    def __init__(self):
        self.data = {
            "sus": {1, 1000},
            "guest": {2, 2000},
            "jack05": {3, 100}
        }
        self.curr_client_id = 4

    def get_balance_by_name(self, client_name):
        return self.data.get(client_name)

    def create_client(self, client_name):
        self.data[client_name] = {self.START_BALANCE, self.curr_client_id}
        self.curr_client_id += 1
        return self.START_BALANCE
