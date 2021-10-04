from core.advbase import *


class Bellina(Adv):
    def s2_before(self, e):
        if self.hp > 30 and e.group == "default":
            self.dragonform.charge_utprep("s2", 0.5 * (self.hp - 30))


variants = {None: Bellina}
