from core.advbase import *
from module.template import LowerMCAdv


class Victor_RNG(Adv):
    conf = {"mbleed": False}


class Victor_50MC(LowerMCAdv):
    pass


variants = {None: Adv, "50MC": Victor_50MC, "RNG": Victor_RNG}
