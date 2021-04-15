from core.advbase import *


class Gala_Mym(Adv):
    def prerun(self):
        Event("dragon").listener(self.a1_on, order=0)

    def a1_on(self, e):
        if self.dragonform.shift_count == 1:
            # quirk in order of "dragon" event means this isnt called before the check for mod
            self.dragonform.shift_spd_mod = Modifier("flamewyrm_spd", "spd", "passive", 0.15).off()
        if self.dragonform.shift_count == 2:
            self.dragonform.conf.update(self.conf.dragonform2)


variants = {None: Gala_Mym}
