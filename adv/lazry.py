from core.advbase import *
from module.template import StanceAdv, LowerMCAdv


class Lazry(StanceAdv):
    def prerun(self):
        self.config_stances(
            {
                "low": ModeManager(group="low", s1=True, s2=True),
                "high": ModeManager(group="high", s1=True, s2=True),
            },
            hit_threshold=0,
        )
        if self.MC is None:
            Event("s").listener(self.a1_amp)
            Event("ds").listener(self.a1_amp)

    def a1_amp(self, e):
        if not self.is_set_cd("a1_amp", 30):
            self.add_amp(max_level=2)


class Lazry_50MC(Lazry, LowerMCAdv):
    pass


variants = {None: Lazry, "50MC": Lazry_50MC}
