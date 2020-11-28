from core.advbase import *

class Gala_Leonidas(Adv):        
    def prerun(self):
        self.draconian_grace = Selfbuff('draconian_grace', 0.0, 0.0, 'att', 'buff')
        self.draconian_grace_level = 0
        self.draconian_grace_dtime = Modifier('draconian_grace_dtime', 'dt', 'leonidas', -0.5)
        self.draconian_grace_endshift = Listener('dragon_end', self.reset_draconian_grace).off()
    
    def upgrade_draconian_grace(self):
        if self.draconian_grace_level >= 5:
            return
        self.draconian_grace_level += 1
        if self.draconian_grace_level > 3:
            self.draconian_grace.value(0.10)
        elif self.draconian_grace_level > 1:
            self.draconian_grace.value(0.05)
        else:
            self.draconian_grace.value(0.0)
        if self.draconian_grace_level == 5:
            self.draconian_grace.off()
            self.draconian_grace.on(-1)
            self.dragonform.shift_cost = 250
            self.draconian_grace_dtime.on()
            self.draconian_grace_endshift.on()
            self.draconian_grace_endtimer = Timer(self.reset_draconian_grace, 40*self.base_buff._bufftime()).on()
        else:
            self.draconian_grace.on(40)

    def reset_draconian_grace(self, t=None):
        self.dragonform.shift_cost = 500
        self.draconian_grace_dtime.off()
        self.draconian_grace_level = 0
        self.draconian_grace.off()
        self.draconian_grace_endshift.off()
        self.draconian_grace_endtimer.off()

    def s2_hit1(self, name, base, group, aseq):
        self.upgrade_draconian_grace()

variants = {None: Gala_Leonidas}