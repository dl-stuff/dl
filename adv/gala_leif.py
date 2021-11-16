from core.advbase import *
from module.template import StanceAdv, LowerMCAdv


class Gala_Leif(StanceAdv):
    def prerun(self):
        self.config_stances(
            {
                "striking": ModeManager(group="striking", x=True, s1=True, s2=True),
                "shielding": ModeManager(group="shielding", x=True, s1=True, s2=True),
            },
            hit_threshold=5,
        )
        if self.MC is None:
            Event("s").listener(self.a1_amp)

    def a1_amp(self, e):
        if not self.is_set_cd("a1_amp", 30):
            self.add_amp(max_level=3)


class Gala_Leif_50MC(Gala_Leif, LowerMCAdv):
    pass


variants = {None: Gala_Leif, "50MC": Gala_Leif_50MC}
