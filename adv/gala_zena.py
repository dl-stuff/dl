from core.advbase import *


class Gala_Zena(Adv):
    def prerun(self):
        self.auspex_gauge = 0
        self.a3_modifier = Modifier("zena_a3", "att", "passive", 0.0)
        self.a3_modifier.get = self.a3_get
        self.fs_alt = FSAltBuff("a1_auspex", "auspex", uses=1)
        # ExAbility hp does not work for A3
        self.passive_hp = self.sub_mod("maxhp", "passive")
        for coab in self.slots.c.coabs.values():
            for ex in coab["ex"]:
                if ex[0] == "hp":
                    self.passive_hp -= ex[1]

    def hitattr_make(self, name, base, group, aseq, attr, onhit=None):
        self.update_auspex(attr.get("cp", 0))
        super().hitattr_make(name, base, group, aseq, attr, onhit=onhit)

    def update_auspex(self, delta):
        if not self.fs_alt.get():
            self.auspex_gauge += delta
        if self.auspex_gauge >= 100:
            self.fs_alt.on()
            self.auspex_gauge = 0

    @property
    def auspex_count(self):
        return self.auspex_gauge // 50

    def a3_get(self):
        if self.hp > 70:
            return self.passive_hp * ((self.hp - 70) / 30 * 0.5 + 0.5)
        else:
            return self.passive_hp * (self.hp / 70 * 0.4 + 0.1)


variants = {None: Gala_Zena}
