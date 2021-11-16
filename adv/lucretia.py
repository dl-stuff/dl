from core.advbase import *


class Lucretia(Adv):
    def s1_proc(self, e):
        if e.name in self.energy.active:
            Teambuff(f"{e.name}_cc", 0.1, 30, "crit", "chance").on()


variants = {None: Lucretia}
