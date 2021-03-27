from core.advbase import *
from module.template import DivineShiftAdv


class Gala_Notte(DivineShiftAdv):
    def prerun(self):
        self.configure_divine_shift("metamorphosis", max_gauge=1800, shift_cost=560, drain=65)


class Gala_Notte_DDAMAGE(Gala_Notte):
    def prerun(self):
        self.configure_divine_shift(
            "metamorphosis",
            max_gauge=1800,
            shift_cost=560,
            drain=65,
            buffs=[Selfbuff("metamorphosis", self.dragonform.ddamage(), -1, "att", "dragon")],
        )
        self.comment = "if dragon damage worked on notte"


variants = {None: Gala_Notte, "DDAMAGE": Gala_Notte_DDAMAGE}
