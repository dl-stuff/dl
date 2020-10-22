from core.advbase import *

class Sharpshooter_Joe(Adv):
    def prerun(self):
        Event('dodge').listener(self.a1_dodge_crit)
        self.a1_cd = False

    def a1_cd_end(self, _):
        self.a1_cd = False

    def a1_dodge_crit(self, e):
        if not self.a1_cd:
            Selfbuff('dodge_crit', 0.08, 10, 'crit', 'chance').on()
            self.a1_cd = True
            Timer(self.a1_cd_end).on(4.999)

variants = {None: Sharpshooter_Joe}
