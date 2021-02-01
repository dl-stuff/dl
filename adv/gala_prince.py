from core.advbase import *

class Gala_Prince(Adv):    
    def prerun(self):
        self.s2.autocharge_init(32000).on()
        if self.condition('draconic charge'):
            self.dragonform.dragon_gauge += 500
        Modifier('dragonlight_dt','dt','hecc',1/0.7-1).on()
        self.dragonform.shift_spd_mod = Modifier('dragonlight_spd', 'spd', 'buff', 0.10).off()

variants = {None: Gala_Prince}
