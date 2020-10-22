from core.advbase import *

class Grace(Adv):
    def prerun(self):
        self.hp = 100

variants = {None: Grace}
