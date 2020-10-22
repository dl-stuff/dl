from core.advbase import *

class Naveed(Adv):
    def prerun(self):
        self.naveed_bauble = 0

    def s2_proc(self, e):
        if self.naveed_bauble < 5:
            self.naveed_bauble += 1

variants = {None: Naveed}
