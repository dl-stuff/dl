from core.advbase import *
from conf import DEFAULT


class Aldred(Adv):
    def s2_before(self, e):
        if self.hp > 30 and e.group == DEFAULT:
            self.dragonform.charge_utprep("s2", 0.5 * (self.hp - 30))


variants = {None: Aldred}
