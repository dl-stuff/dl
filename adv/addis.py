from core.advbase import *


class Addis_RNG(Adv):
    conf = {"mbleed": False}


variants = {None: Adv, "RNG": Addis_RNG}
