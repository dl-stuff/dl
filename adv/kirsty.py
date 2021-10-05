from core.advbase import *
from module.template import LowerMCAdv


class Kirsty(Adv):
    def prerun(self):
        if self.condition("maintain Grand Strategist"):
            Timer(self.a1_proc).on(10)
            Timer(self.a1_proc).on(20)
            Timer(self.a1_proc).on(30)

    def a1_proc(self, t):
        Selfbuff("grand_strategist", 0.25, -1).on()
        AffEdgeBuff("grand_strategist_affedge", 0.2, -1, "poison").on()


class Kirsty_50MC(Kirsty, LowerMCAdv):
    def prerun(self):
        if not self.nihilism and self.condition("maintain Dauntless Strength"):
            Timer(self.a1_proc).on(15)
            Timer(self.a1_proc).on(30)
            Timer(self.a1_proc).on(45)

    def a1_proc(self, t):
        Selfbuff("dauntless_strength", 0.20, -1).on()


variants = {None: Kirsty, "50MC": Kirsty_50MC}
