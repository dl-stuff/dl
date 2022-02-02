from core.advbase import *
from module.template import LowerMCAdv


class Gala_Sarisse(Adv):
    def prerun(self):
        self.ahits = 0

    def add_combo(self, name="#"):
        result = super().add_combo(name)
        if self.nihilism:
            return result
        if self.condition("always connect hits"):
            a_hits = self.hits // 20
            if a_hits > 0 and a_hits != self.ahits:
                self.ahits = a_hits
                Selfbuff("a1_att", 0.02, 15, "att", "buff", source=name).on()
                Selfbuff("a1_crit", 0.01, 15, "crit", "chance", source=name).on()
        return result


class Gala_Sarisse_50MC(LowerMCAdv):
    pass


variants = {None: Gala_Sarisse, "50MC": Gala_Sarisse_50MC}
