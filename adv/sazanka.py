from core.advbase import *


class Sazanka_RNG(Adv):
    conf = {"mbleed": False}


variants = {None: Adv, "RNG": Sazanka_RNG}
