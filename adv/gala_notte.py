from core.advbase import *


class Gala_Notte_DDAMAGE(Adv):
    comment = "if dragon damage worked on notte"
    SAVE_VARIANT = False

    def prerun(self):
        self.dragonform.shift_mods.append(self.dragonform.dracolith_mod)


class Gala_Notte_INFMETA(Adv):
    comment = "infinite metamorphosis gauge"
    SAVE_VARIANT = False

    def prerun(self):
        self.dragonform.set_utp_infinite()


variants = {None: Adv, "DDAMAGE": Gala_Notte_DDAMAGE, "INFMETA": Gala_Notte_INFMETA}
