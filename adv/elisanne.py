from core.advbase import *
from module.template import LowerMCAdv


class Elisanne(Adv):
    conf = {}
    conf["prefer_baseconf"] = True
    conf["share"] = ["Weapon", "Xania"]
    conf["acl"] = [
        "`s1",
    ]


class Elisanne_55MC(LowerMCAdv):
    MC = 55


variants = {None: Elisanne, "55MC": Elisanne_55MC}
