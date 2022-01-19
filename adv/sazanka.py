from core.advbase import *
from module.template import LowerMCAdv


class Sazanka_RNG(Adv):
    conf = {"mbleed": False}


class Sazanka_50MC(LowerMCAdv):
    pass


variants = {None: Adv, "50MC": Sazanka_50MC, "RNG": Sazanka_RNG}
