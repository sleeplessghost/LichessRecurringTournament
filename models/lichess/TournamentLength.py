from enum import StrEnum

class TournamentLength(StrEnum):
    MINUTES_20 = '20'
    MINUTES_25 = '25'
    MINUTES_30 = '30'
    MINUTES_35 = '35'
    MINUTES_40 = '40'
    MINUTES_45 = '45'
    MINUTES_50 = '50'
    MINUTES_55 = '55'
    MINUTES_60 = '60'
    MINUTES_70 = '70'
    MINUTES_80 = '80'
    MINUTES_90 = '90'
    MINUTES_100 = '100'
    MINUTES_110 = '110'
    MINUTES_120 = '120'
    MINUTES_150 = '150'
    MINUTES_180 = '180'
    MINUTES_210 = '210'
    MINUTES_240 = '240'
    MINUTES_270 = '270'
    MINUTES_300 = '300'
    MINUTES_330 = '330'
    MINUTES_360 = '360'
    MINUTES_420 = '420'
    MINUTES_480 = '480'
    MINUTES_540 = '540'
    MINUTES_600 = '600'
    MINUTES_720 = '720'

    def int_val(self):
        return int(self.value)