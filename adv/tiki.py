from core.advbase import *


class Tiki_DDAMAGE(Adv):
    comment = "if dragon damage worked on tiki"
    SAVE_VARIANT = False

    def prerun(self):
        self.dragonform.shift_mods.append(self.dragonform.dracolith_mod)


class Tiki_INFDRGN(Adv):
    SAVE_VARIANT = False
    comment = "infinite divine shift gauge"

    def prerun(self):
        self.dragonform.set_utp_infinite()


variants = {None: Adv, "DDAMAGE": Tiki_DDAMAGE, "INFDRGN": Tiki_INFDRGN}
