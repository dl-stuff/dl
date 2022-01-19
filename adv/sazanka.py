from core.advbase import *


class Sazanka_RNG(Adv):
    conf = {"mbleed": False}


class Sazanka_50MC(Adv, LowerMCAdv):
    pass


variants = {None: Adv, "50MC": Sazanka_50MC, "RNG": Sazanka_RNG}
