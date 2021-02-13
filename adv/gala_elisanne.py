from core.advbase import *


class Gala_Elisanne(Adv):
    def prerun(self):
        self.s2.autocharge_init(960).on()


variants = {None: Gala_Elisanne}
