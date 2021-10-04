from core.advbase import *


class Luther(Adv):
    def prerun(self):
        self.fs_alt = FSAltBuff(group="enhanced", uses=1)
        Timer(self.fs_alt_on_crit, 10, True).on()

    def fs_alt_on_crit(self, t):
        # look i dont wanna mass sim
        self.fs_alt.on()


variants = {None: Luther}
