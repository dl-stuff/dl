from core.advbase import *


class Kirsty(Adv):
    def prerun(self):
        if not self.nihilism and self.condition("maintain Dauntless Strength"):
            Timer(self.dauntless_strength).on(15)
            Timer(self.dauntless_strength).on(30)
            Timer(self.dauntless_strength).on(45)

    def dauntless_strength(self, t):
        Selfbuff("dauntless_strength", 0.20, -1).on()


variants = {None: Kirsty}
