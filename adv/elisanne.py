from core.advbase import *
from module.template import LowerMCAdv


class Elisanne(Adv):
    conf = {}
    conf["prefer_baseconf"] = True
    conf["acl"] = [
        "`s2",
    ]


class Elisanne_55MC(LowerMCAdv):
    MC = 55


variants = {None: Elisanne, "55MC": Elisanne_55MC}
