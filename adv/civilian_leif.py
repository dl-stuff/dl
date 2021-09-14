from core.advbase import *


class Civilian_Leif_RNG(Adv):
    conf = {"mbleed": False}


variants = {None: Adv, "RNG": Civilian_Leif_RNG}
