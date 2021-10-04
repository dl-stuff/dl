from core.advbase import *


class Forte(Adv):
    def prerun(self):
        Event("s").listener(self.s_dgauge)

    def s_dgauge(self, e):
        if e.name != "ds":
            self.dragonform.charge_prep(4)


variants = {None: Forte}
