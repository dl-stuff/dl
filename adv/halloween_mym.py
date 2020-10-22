from core.advbase import *

class Halloween_Mym(Adv):
    def prerun(self):
        self.a3_da = Selfbuff('a3_dreamboost',0.20,15,'da','passive')
        self.dragonform.shift_spd_mod = Modifier('flamewyrm_spd', 'spd', 'passive', 0.15).off()

    @staticmethod
    def prerun_skillshare(adv, dst):
        adv.a3_da = Dummy()

    def s2_proc(self, e):
        self.a3_da.on()

variants = {None: Halloween_Mym}
