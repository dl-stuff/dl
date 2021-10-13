from core.advbase import *


class Ilia(Adv):
    def prerun(self):
        self.alchemy = 0
        self.cartridge = 0
        o_s2_check = self.a_s_dict["s2"].check
        self.a_s_dict["s2"].check = lambda: o_s2_check() and (self.alchemy > 33 or self.cartridge > 0) and not self.nihilism
        self.cartridge_fs = [
            FSAltBuff("s2_cartridge", "cartridge1", uses=1),
            FSAltBuff("s2_cartridge", "cartridge2", uses=1),
            FSAltBuff("s2_cartridge", "cartridge3", uses=1),
        ]
        self.cartridge_t = Timer(self.l_cartridge_timeout)
        self.uses_combo = True

    def alchemy_bars(self):
        if self.alchemy < 33:
            return 0
        if self.alchemy < 66:
            return 1
        if self.alchemy < 100:
            return 2
        return 3

    def a_update(self, add):
        if self.cartridge == 0:
            if add > 0 and self.hits >= 30:
                add *= 3
            prev_charge = self.alchemy_bars()
            self.alchemy = min(self.alchemy + add, 100)
            if prev_charge < self.alchemy_bars():
                log("alchemy", self.alchemy_bars(), self.alchemy)

    def a_deplete_cartridge(self, name, consume=1):
        if self.cartridge > 0:
            prev_cartridge = self.cartridge
            self.cartridge -= consume
            for i in range(min(3, prev_cartridge - self.cartridge)):
                Selfbuff("a3_crit", 0.3, 15, "crit", "chance").ex_bufftime().on()
            if self.cartridge > 0:
                self.current_s["s1"] = "cartridge3"
                self.current_s["s2"] = "cartridge3"
                self.cartridge_fs[self.cartridge].off()
                self.cartridge_fs[self.cartridge - 1].on()
            else:
                self.current_s["s1"] = "default"
                self.current_s["s2"] = "default"
                for buff in self.cartridge_fs:
                    buff.off()
                self.cartridge_t.off()
            log("cartridge", self.cartridge)

    def l_cartridge_timeout(self, t):
        self.cartridge = 0
        self.current_s["s1"] = "default"
        self.current_s["s2"] = "default"
        for buff in self.cartridge_fs:
            buff.off()

    def hitattr_make(self, name, base, group, aseq, attr, onhit=None, dtype=None):
        add = attr.get("cp")
        if add:
            self.a_update(add)
        super().hitattr_make(name, base, group, aseq, attr, onhit=onhit, dtype=dtype)

    def s1_before(self, e):
        if e.group == "cartridge3":
            self.a_deplete_cartridge(e.name)

    def s2_before(self, e):
        if e.group == "cartridge3":
            self.a_deplete_cartridge(e.name)
        elif not self.nihilism:
            self.cartridge = self.alchemy_bars()
            self.alchemy = 0
            self.cartridge_fs[self.cartridge - 1].on()
            self.cartridge_t.on(20)
            self.current_s["s1"] = "cartridge3"
            self.current_s["s2"] = "cartridge3"

    def fs_cartridge1_before(self, e):
        self.a_deplete_cartridge(e.name, consume=1)

    def fs_cartridge2_before(self, e):
        self.a_deplete_cartridge(e.name, consume=2)

    def fs_cartridge3_before(self, e):
        self.a_deplete_cartridge(e.name, consume=3)


variants = {None: Ilia}
