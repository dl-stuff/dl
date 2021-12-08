from core.advbase import *
from conf import DEFAULT


class Dragonyule_Ilia(Adv):
    def prerun(self):
        self.alchemy = 0
        self.cartridge_loaded = 0
        self.starfall_spirit_buffs = [
            MultiBuffManager(
                "starfall_spirit",
                [
                    Selfbuff("starfall_str", 0.15, 15, "att").ex_bufftime(),
                    Selfbuff("starfall_crit", 0.15, 15, "crit").ex_bufftime(),
                ],
            )
            for _ in range(3)
        ]

    def alchemy_bars(self):
        if self.alchemy < 33:
            return 0
        if self.alchemy < 66:
            return 1
        if self.alchemy < 100:
            return 2
        return 3

    def a_update(self, add):
        prev_charge = self.alchemy_bars()
        self.alchemy = min(self.alchemy + add, 100)
        if prev_charge < self.alchemy_bars():
            self.cartridge_loaded = self.alchemy_bars()
            log("cartridge_loaded", self.cartridge_loaded, self.alchemy)

    def a_deplete_cartridge(self):
        for i in range(min(3, self.cartridge_loaded)):
            if not self.starfall_spirit_buffs[i].get():
                self.starfall_spirit_buffs[i].on()
            log("cartridge_loaded", self.cartridge_loaded)
        self.cartridge_loaded = 0

    def hitattr_make(self, name, base, group, aseq, attr, onhit=None, dtype=None):
        add = attr.get("cp")
        if add:
            self.a_update(add)
        super().hitattr_make(name, base, group, aseq, attr, onhit=onhit, dtype=dtype)

    def s1_proc(self, e):
        self.a_deplete_cartridge()


variants = {None: Dragonyule_Ilia}
