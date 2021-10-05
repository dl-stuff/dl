from core.advbase import *
from module.template import LowerMCAdv


class Summer_Verica(Adv):
    def prerun(self):
        self.s2.autocharge_init(self.s2_autocharge).on()

    def s2_autocharge(self, t):
        if self.s1.sp > self.s1.charged:
            log("sp", "s2_autocharge", 1578)
            self.s2.charge(1578)


class Summer_Verica_50MC(Summer_Verica, LowerMCAdv):
    pass


variants = {None: Summer_Verica, "50MC": Summer_Verica_50MC}
