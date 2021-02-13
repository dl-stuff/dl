from core.advbase import *


class Chelle(Adv):
    def prerun(self):
        Event("dragon_end").listener(self.shift_end_inspiration)

    def shift_end_inspiration(self, e):
        self.inspiration.add(5)


variants = {None: Chelle}
