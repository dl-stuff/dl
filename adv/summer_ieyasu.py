from core.advbase import *


class Summer_Ieyasu(Adv):
    conf = {"mbleed": True}


class Summer_Ieyasu_RNG(Summer_Ieyasu):
    conf = {"mbleed": False}


variants = {None: Summer_Ieyasu, "RNG": Summer_Ieyasu_RNG}
