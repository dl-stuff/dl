from core.advbase import *

class Serena(Adv):
    def prerun(self):
        self.a1_count = 0
        self.a3_count = 0

    def add_combo(self, name='#'):
        super().add_combo(name)
        if self.a1_count < 3 and self.a1_count != self.hits // 20:
            self.a1_count = self.hits // 20
            Selfbuff('a1_cd',0.06,-1,'crit','damage').on()
        if self.a3_count < 3 and self.a3_count != self.hits // 30:
            self.a3_count = self.hits // 30
            Selfbuff('a3_cc',0.03,-1,'crit','chance').on()

variants = {None: Serena}
