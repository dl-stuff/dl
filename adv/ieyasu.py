from core.advbase import *
from module.bleed import Bleed

class Ieyasu(Adv):
    def s2ifbleed(self):
        if self.bleed_stack > 0:
            return self.s2buff.get()
        return 0

    def prerun(self):
        self.s2buff = Selfbuff('s2',0.20,15,'crit')
        self.s2buff.modifier.get = self.s2ifbleed

variants = {None: Ieyasu}
