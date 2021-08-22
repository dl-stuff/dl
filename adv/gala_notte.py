from core.advbase import *
from module.template import DivineShiftAdv


class Gala_Notte(DivineShiftAdv):
    SAVE_VARIANT = False

    def prerun(self):
        self.configure_divine_shift("metamorphosis", max_gauge=1800, shift_cost=560, drain=65)

    def x(self):
        x_min = 1
        prev = self.action.getprev()
        if isinstance(prev, X) and prev.index == 2:
            x_min = 2
        return super().x(x_min=x_min)


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


class Gala_Notte_METAMORPHOSIS(Gala_Notte):
    comment = "infinite metamorphosis gauge"

    def prerun(self):
        self.configure_divine_shift("metamorphosis", max_gauge=1800, shift_cost=560, drain=65, infinite=True)
        self.dragonform.charge_gauge(1800, utp=True, dhaste=False)


variants = {None: Gala_Notte, "DDAMAGE": Gala_Notte_DDAMAGE, "INFMETA": Gala_Notte_METAMORPHOSIS}
