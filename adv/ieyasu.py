from core.advbase import *
from module.bleed import Bleed


class Ieyasu(Adv):
    def s2_ifbleed(self):
        if self.bleed_stack > 0:
            return self.s2_buff.get()
        return 0

    def prerun(self):
        self.s2_buff = Selfbuff("s2", 0.20, 15, "crit")
        self.s2_buff.modifier.get = self.s2_ifbleed

    def s2_proc(self, e):
        if self.nihilism:
            return
        self.s2_buff.on()


variants = {None: Ieyasu}
