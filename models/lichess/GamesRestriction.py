from enum import Enum

class GamesRestriction(str, Enum):
    NONE = 'none'
    GAMES_0 = '0'
    GAMES_5 = '5'
    GAMES_10 = '10'
    GAMES_15 = '15'
    GAMES_20 = '20'
    GAMES_30 = '30'
    GAMES_40 = '40'
    GAMES_50 = '50'
    GAMES_75 = '75'
    GAMES_100 = '100'
    GAMES_150 = '150'
    GAMES_200 = '200'

    def int_val(self):
        return int(self.value)