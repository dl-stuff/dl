from core.advbase import *


class Summer_Ieyasu_RNG(Adv):
    conf = {"mbleed": False}


variants = {None: Adv, "RNG": Summer_Ieyasu_RNG}
