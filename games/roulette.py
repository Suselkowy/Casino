from games.gameClass import Game, GameStatus

class Roulette(Game):
    MAX_PLAYERS = 100
    MIN_PLAYERS = 1

    def __init__(self):
        super().__init__()

    def handle_response(self, response, s):
        super(Roulette, self).handle_response(response, s)
        if self.status != GameStatus.STOPPED:
            pass
    