from core.advbase import *


class Gala_Notte_DDAMAGE(Adv):
    comment = "if dragon damage worked on notte"

    def prerun(self):
        self.dragonform.shift_mods.append(self.dragonform.dracolith_mod)


class Gala_Notte_INFMETA(Adv):
    comment = "infinite metamorphosis gauge"

    def prerun(self):
        self.dragonform.drain = -1


variants = {None: Adv, "DDAMAGE": Gala_Notte_DDAMAGE, "INFMETA": Gala_Notte_INFMETA}
