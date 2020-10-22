from core.advbase import *

class Sha_Wujing(Adv):
    def prerun(self):
        self.a1_count = 3
        Timer(self.a3_start).on(self.duration*0.3)
        Event('s').listener(self.a1_check, order=2)

    def a3_start(self, t):
        Selfbuff('a3', 0.08, -1, 'att', 'assailant').on()

    def a1_check(self, e):
        if self.a1_count > 0:
            self.a1_count -= 1
            Selfbuff('a1', 0.06, -1, 's', 'buff').on()

variants = {None: Sha_Wujing}
