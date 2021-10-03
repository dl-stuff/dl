from core.advbase import *
from module.template import RngCritAdv


class Mikoto(RngCritAdv):
    def prerun(self):
        if not self.nihilism:
            self.config_rngcrit(cd=15, ev=20)
            self.a1_stack = 0
            self.a1_sp_mod = Modifier("a1_sp_mod", "sp_s1", "passive", 0.0)

    def rngcrit_cb(self, mrate=None):
        self.a1_stack = mrate
        self.a1_sp_mod.mod_value = 0.1 * self.a1_stack

    @property
    def buffcount(self):
        buffcount = super().buffcount
        return buffcount + self.a1_stack


variants = {None: Mikoto}
