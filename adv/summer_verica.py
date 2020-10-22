from core.advbase import *

class Summer_Verica(Adv):
    def prerun(self):
        self.s2.autocharge_init(self.s2_autocharge).on()

    def s2_autocharge(self, t):
        if self.s1.sp > self.s1.charged:
            log('s2', 1578)
            self.s2.charge(1578)

variants = {None: Summer_Verica}
