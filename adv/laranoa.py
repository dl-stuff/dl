from core.advbase import *


class Laranoa(Adv):
    comment = "no haste buff for teammates"

    def prerun(self):
        self.ahits = 0

    def add_combo(self, name="#"):
        result = super().add_combo(name)
        if self.condition("always connect hits"):
            a_hits = self.hits // 15
            if a_hits > 0 and a_hits != self.ahits:
                self.ahits = a_hits
                Selfbuff("a1_crit_dmg", 0.10, 20, "crit", "damage", source=name).on()
        return result


variants = {None: Laranoa}
