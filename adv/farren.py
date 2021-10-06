from core.advbase import *


class Farren(Adv):
    def prerun(self):
        self.a3_regen = Timer(self.a3_regen, 1.0, True).on()

    def s2_proc(self, e):
        if e.group == "default":
            self.add_hp(140 * self.dragonform.utp_gauge / self.dragonform.max_utp_gauge)
            self.dragonform.charge_utprep(e.name, -100)

    def a3_regen(self, t):
        if self.amp_lvl(kind="team", key=3) >= 1:
            self.dragonform.charge_utprep("a3", 1.5)


variants = {None: Farren}
