from enum import StrEnum

class NameReplacement(StrEnum):
    WINNER = '[winner]'

class TemplateReplacement(StrEnum):
    NAME = '[name]'
    VARIANT = '[variant]'
    CLOCKTIME = '[clocktime]'
    INCREMENT = '[clockincrement]'
    LINK = '[link]'
    BREAK = '[br]'
    TIMEZONE = '\[timezone:\S+\]' #regex match, used like [timezone:Europe/London]