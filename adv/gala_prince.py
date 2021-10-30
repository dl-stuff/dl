from core.advbase import *
from module.template import LowerMCAdv


class Gala_Prince(Adv):
    DRAGONLIGHT_DT = 1 / 0.6 - 1

    def prerun(self):
        if self.condition("draconic charge"):
            self.dragonform.charge_dprep(500)
        Modifier("dragonlight_dt", "dt", "getrektoof", self.DRAGONLIGHT_DT).on()
        self.dragonform.shift_spd_mod = Modifier("dragonlight_spd", "spd", "buff", 0.10).off()


class Gala_Prince_50MC(Gala_Prince, LowerMCAdv):
    DRAGONLIGHT_DT = 1 / 0.7 - 1


variants = {None: Gala_Prince, "50MC": Gala_Prince_50MC}
