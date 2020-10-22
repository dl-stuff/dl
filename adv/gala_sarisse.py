from core.advbase import *

class Gala_Sarisse(Adv):
    def prerun(self):
        self.ahits = 0
        self.s2stance = 0

    def add_combo(self, name='#'):
        super().add_combo(name)
        if self.condition('always connect hits'):
            if self.hits // 20 > self.ahits:
                self.ahits = self.hits // 20
                Selfbuff('a1_att',0.02,15,'att','buff', source=name).on()
                Selfbuff('a1_crit',0.01,15,'crit','chance', source=name).on()

variants = {None: Gala_Sarisse}
