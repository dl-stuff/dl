from core.advbase import *

class Yoshitsune(Adv):
    comment = 'no counter on s1'
    
    def prerun(self):
        Event('dodge').listener(self.l_dodge_attack, order=0)
        self.dodge_aspd = Selfbuff('dodge_aspd', 0.10, 30, 'spd', 'buff').ex_bufftime()
        # self.a1_cd = False
        self.a1_cd = True

    def a1_cd_end(self, _):
        self.a1_cd = False

    def l_dodge_attack(self, e):
        log('cast', 'd')
        for _ in range(7):
            self.dmg_make('dodge', 0.10)
        if not self.a1_cd:
            self.a1_cd = True
            Timer(self.a1_cd_end).on(4.999)
            self.dodge_aspd.on()


variants = {None: Yoshitsune}
