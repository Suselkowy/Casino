class InvalidResponseException(Exception):
    def __init__(self):
        self.message = "Provided response was not valid"

class InvalidUserException(Exception):
    def __init__(self):
        self.message = "Provided user does not exists"

class InvalidGameName(Exception):
    def __init__(self):
        self.message = "Game does not exists"