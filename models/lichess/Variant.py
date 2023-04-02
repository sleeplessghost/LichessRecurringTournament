from enum import Enum

class Variant(Enum):
    STANDARD = "standard"
    CHESS960 = "chess960"
    CRAZYHOUSE = "crazyhouse"
    ANTICHESS = "antichess"
    ATOMIC = "atomic"
    HORDE = "horde"
    KING_OF_THE_HILL = "kingOfTheHill"
    RACING_KINGS = "racingKings"
    THREE_CHECK = "threeCheck"
    FROM_POSITION = "fromPosition"