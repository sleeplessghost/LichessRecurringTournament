import random
from rich import print

HAPPY_FACES = [
    '(´・ω・｀)',
    '( ´･ω･)',
    '( ´･ω･)人(・ω・｀ )',
    '(｀･ω･)ﾉ☆･ﾟ::ﾟ',
    '(｡´・ω・｀｡)',
    '（*＾ワ＾*）',
    '(๑꧆◡꧆๑)',
    'ヾ(＠^∇^＠)ノ',
    'o(〃＾▽＾〃)o',
    '(✧Д✧) YES!!',
    'ヽ(＾Д＾)ﾉ',
    '（｡>‿‿<｡ ）',
    '(〃 ω 〃)',
    '(🖒^_^)🖒',
    ' (☆｀• ω •´)ｂ'
]
SAD_FACES = [
    '(´；д；`)',
    '(　；∀；)',
    '(´；ω；`)',
    '(ಥ‿ಥ)',
    '(╥﹏╥)',
    '(ㄒoㄒ)',
    'o(TヘTo)',
    '（┬┬＿┬┬）',
    '(´；д；)',
    '(ᗒᗩᗕ)'
]

def success(message: str = ''):
    print(f'{random.choice(HAPPY_FACES)} {message}')

def failure(message: str = ''):
    print(f'{random.choice(SAD_FACES)} {message}')