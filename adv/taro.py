from core.advbase import *

class Taro(Adv):
    conf = {'mbleed': True}

class Taro_RNG(Taro):
    conf = {'mbleed': False}

variants = {
    None: Taro,
    'RNG': Taro_RNG
}