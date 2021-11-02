from core.advbase import *


class Dragonyule_Nefaria(Adv):
    def x_proc(self, e):
        if self.hits >= 15:
            self.afflics.freeze.on(f"{e.name}_flurry_freezer", 0.25)
            

variants = {None: Dragonyule_Nefaria}
