from core.advbase import *
from module.template import RngCritAdv


class Incognito_Nefaria(RngCritAdv):
    def prerun(self):
        self.config_rngcrit(cd=7, ev=20)
        self.a1_buff = Selfbuff("a1", 0, 20, "crit", "damage")
        self.a1_stack = 0

    def rngcrit_cb(self, mrate=None):
        new_value = 0.20 * mrate
        if not self.a1_buff:
            self.a1_buff.set(new_value)
            self.a1_buff.on()
        else:
            self.a1_buff.value(new_value)
        self.a1_stack = mrate - 1

    @property
    def buffcount(self):
        buffcount = super().buffcount
        return buffcount + self.a1_stack


variants = {None: Incognito_Nefaria}
