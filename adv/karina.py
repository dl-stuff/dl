from core.advbase import *


class Karina_FLEET(Adv):
    comment = "4 Karina comp"
    conf = {"fleet": 3}
    conf["prefer_baseconf"] = True


variants = {None: Adv, "FLEET": Karina_FLEET}
