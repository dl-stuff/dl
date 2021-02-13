from core.advbase import *


class Delphi(Adv):
    def prerun(self):
        self.s1.autocharge_init(80000).on()
        self.s2.autocharge_init(50000).on()


variants = {None: Delphi}
