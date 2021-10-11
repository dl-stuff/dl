from core.advbase import *


class Alberius(Adv):
    def prerun(self):
        Event("x").listener(self.dragons_fierce_rule)
        Event("s").listener(self.dragons_fierce_rule)

    def dragons_fierce_rule(self, e):
        if self.in_dform():
            self.dispel()


variants = {None: Alberius}
