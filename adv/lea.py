from core.advbase import *
from module.template import LowerMCAdv


class Lea(Adv):
    def s2_before(self, e):
        self.hp_before_s2 = self._hp

    def s2_proc(self, e):
        log("dmg", "#reflect", (self.hp_before_s2 - self._hp) * 11, "reflect")


class Lea_50MC(Lea, LowerMCAdv):
    pass


variants = {None: Lea, "50MC": Lea_50MC}
