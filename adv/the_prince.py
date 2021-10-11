from core.advbase import *


class The_Prince(Adv):
    def prerun(self):
        Event("x").listener(self.dragons_dominance)

    def dragons_dominance(self, e):
        if self.in_dform():
            self.dispel()


variants = {None: The_Prince}
