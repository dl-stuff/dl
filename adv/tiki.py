from core.advbase import *
from module.template import DivineShiftAdv


class Tiki(DivineShiftAdv):
    def prerun(self):
        self.configure_divine_shift("divine_dragon", max_gauge=1800, shift_cost=560, drain=40)


class Tiki_DDAMAGE(Tiki):
    SAVE_VARIANT = False

    def prerun(self):
        self.configure_divine_shift(
            "divine_dragon",
            max_gauge=1800,
            shift_cost=560,
            drain=40,
            buffs=[Selfbuff("divine_dragon", self.dragonform.ddamage(), -1, "att", "dragon")],
        )
        self.comment = "if dragon damage worked on tiki"


class Tiki_INF_SHIFT(Tiki):
    SAVE_VARIANT = False
    comment = "infinite divine shift gauge"

    def prerun(self):
        self.configure_divine_shift("divine_dragon", max_gauge=1800, shift_cost=0, drain=0)
        self.dragonform.charge_gauge(1800, utp=True, dhaste=False)


variants = {None: Tiki, "DDAMAGE": Tiki_DDAMAGE, "INFDRGN": Tiki_INF_SHIFT}
