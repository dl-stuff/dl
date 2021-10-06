from core.advbase import *


class Forte(Adv):
    def prerun(self):
        Event("s").listener(self.s_dgauge)

    def s_dgauge(self, e):
        if e.base in ("s1", "s2", "s3", "s4"):
            self.dragonform.charge_dprep(4)


variants = {None: Forte}
