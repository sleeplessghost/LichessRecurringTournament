from enum import StrEnum

class ClockIncrement(StrEnum):
    SECONDS_0 = '0'
    SECONDS_1 = '1'
    SECONDS_2 = '2'
    SECONDS_3 = '3'
    SECONDS_4 = '4'
    SECONDS_5 = '5'
    SECONDS_6 = '6'
    SECONDS_7 = '7'
    SECONDS_10 = '10'
    SECONDS_15 = '15'
    SECONDS_20 = '20'
    SECONDS_25 = '25'
    SECONDS_30 = '30'
    SECONDS_40 = '40'
    SECONDS_50 = '50'
    SECONDS_60 = '60'

    def int_val(self):
        return int(self.value)