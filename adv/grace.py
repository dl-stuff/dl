from core.advbase import *


class Grace(Adv):
    def prerun(self):
        self.set_hp(100)


variants = {None: Grace}
