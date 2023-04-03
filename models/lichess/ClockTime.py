from enum import StrEnum

class ClockTime(StrEnum):
    SECONDS_0 = '0'
    SECONDS_15 = '0.25'
    SECONDS_30 = '0.5'
    SECONDS_45 = '0.75'
    MINUTES_1 = '1'
    MINUTES_1_HALF = '1.5'
    MINUTES_2 = '2'
    MINUTES_3 = '3'
    MINUTES_4 = '4'
    MINUTES_5 = '5'
    MINUTES_6 = '6'
    MINUTES_7 = '7'
    MINUTES_8 = '8'
    MINUTES_10 = '10'
    MINUTES_15 = '15'
    MINUTES_20 = '20'
    MINUTES_25 = '25'
    MINUTES_30 = '30'
    MINUTES_40 = '40'
    MINUTES_50 = '50'
    MINUTES_60 = '60'

    def float_val(self):
        return float(self.value)