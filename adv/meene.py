from core.advbase import *
from module.template import ButterflyAdv


class Meene(ButterflyAdv):
    def prerun(self):
        self.config_butterflies()

    def s1_proc(self, e):
        self.clear_all_butterflies()

    def s2_proc(self, e):
        self.clear_all_butterflies()


variants = {None: Meene}
