from core.advbase import *

class Gala_Mym(Adv):    
    def prerun(self):
        self.a1_buff = MultiBuffManager('flamewyrm', buffs=[
            Selfbuff('flamewyrm', 0.15, -1, 'att', 'buff'),
            SAltBuff(group='flamewyrm', base='s2')
        ])
        Event('dragon').listener(self.a1_on)

    def a1_on(self, e):
        if not self.a1_buff.get():
            self.a1_buff.on()
        else:
            self.dragonform.conf.update(self.conf.dragonform2)
            self.dragonform.shift_spd_mod = Modifier('flamewyrm_spd', 'spd', 'buff', 0.15).off()

variants = {None: Gala_Mym}
