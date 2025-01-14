from enum import StrEnum

class RatingRestriction(StrEnum):
    NONE = 'none'
    RATING_1000 = '1000'
    RATING_1100 = '1100'
    RATING_1200 = '1200'
    RATING_1300 = '1300'
    RATING_1400 = '1400'
    RATING_1500 = '1500'
    RATING_1600 = '1600'
    RATING_1700 = '1700'
    RATING_1800 = '1800'
    RATING_1900 = '1900'
    RATING_2000 = '2000'
    RATING_2100 = '2100'
    RATING_2200 = '2200'
    RATING_2300 = '2300'
    RATING_2400 = '2400'
    RATING_2500 = '2500'
    RATING_2600 = '2600'

    def int_val(self):
        return int(self.value)