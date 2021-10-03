from core.advbase import *


class Gala_Mym(Adv):
    def prerun(self):
        Event("dragon").listener(self.a1_on, order=0)

    def a1_on(self, e):
        if self.dshift_count == 1:
            # "dragon" event is called after spd mod check in d_shift_start so this is ok
            self.dragonform.shift_spd_mod = Modifier("flamewyrm_spd", "spd", "passive", 0.15).off()
        if self.dshift_count == 2:
            for act in self.dragonform.conf.values():
                try:
                    if act["attr"] and act["attr_HAS"]:
                        act["attr"] = act["attr_HAS"]
                except TypeError:
                    pass


variants = {None: Gala_Mym}
