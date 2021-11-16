from core.advbase import *


class Dragonyule_Lily(Adv):
    def prerun(self):
        self.starfall_strength = 0

    def fs_dragonyulelily_proc(self, e):
        self.starfall_strength = min(3, self.starfall_strength + 1)

    def s2_proc(self, e):
        self.starfall_strength = 0


variants = {None: Dragonyule_Lily}
