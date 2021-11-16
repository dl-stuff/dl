from core.advbase import *


class Taro_RNG(Adv):
    conf = {"mbleed": False}


variants = {None: Adv, "RNG": Taro_RNG}
