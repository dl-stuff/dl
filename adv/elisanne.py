from core.advbase import *
from module.template import LowerMCAdv


class Elisanne_55MC(LowerMCAdv):
    MC = 55


variants = {None: Adv, "55MC": Elisanne_55MC}
