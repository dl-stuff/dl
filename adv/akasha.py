from core.advbase import *
from module.template import LowerMCAdv


class Akasha(Adv):
    def prerun(self):
        super().prerun()
        if self.MC is None:
            Event("s").listener(self.a1_amp)

    def a1_amp(self, e):
        if not self.is_set_cd("a1_amp", 30):
            self.add_amp(max_level=2)


variants = {None: Akasha, "50MC": LowerMCAdv}
