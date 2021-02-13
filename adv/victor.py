from core.advbase import *


class Victor_RNG(Adv):
    conf = {"mbleed": False}


variants = {None: Adv, "RNG": Victor_RNG}
