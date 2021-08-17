from core.advbase import *


class Naveed(Adv):
    def prerun(self):
        self.naveed_bauble = 0

    def s2_proc(self, e):
        if self.naveed_bauble < 5:
            self.naveed_bauble += 1


class Naveed_MAX_BAUBLES(Naveed):
    SAVE_VARIANT = False
    comment = "5 stacks radiant bauble"

    def prerun(self):
        self.naveed_bauble = 5


variants = {None: Naveed, "MAX_BAUBLES": Naveed_MAX_BAUBLES}
