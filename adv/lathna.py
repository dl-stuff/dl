from core.advbase import *
from conf import DEFAULT


class Lathna(Adv):
    def prerun(self):
        self.dragonform.shift_mods.append(Modifier("faceless_god", "poison_killer", "passive", 2.00).off())
        Event("dragon").listener(self.dshift_heal)

    def dshift_heal(self, e):
        Selfbuff("lathna_regen", 14, 20, "regen", "buff", source="dshift").on()

    @staticmethod
    def prerun_skillshare(adv, dst):
        adv.current_s[dst] = "all"

    @allow_acl
    def s(self, n, s1_kind=None):
        if self.in_dform():
            return False
        if n == 1 and s1_kind == "all":
            self.current_s["s1"] = "all"
        else:
            self.current_s["s1"] = DEFAULT
        return super().s(n)


variants = {None: Lathna}
