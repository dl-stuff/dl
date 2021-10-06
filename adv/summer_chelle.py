from core.advbase import *


class Summer_Chelle(Adv):
    def prerun(self):
        self.radiance_gauge = 0
        Event("dragon").listener(self.reset_radiance)
        self.a1_modifier = Modifier("radiance_flashburn", "edge", "flashburn", 0.0)
        self.afflics.flashburn.aff_edge_mods.append(self.a1_modifier)
        self.a1_modifier.get = self.a1_get

    @staticmethod
    def prerun_skillshare(adv, dst):
        adv.radiance_gauge = 0

    def hitattr_make(self, name, base, group, aseq, attr, onhit=None, dtype=None):
        self.update_radiance(attr.get("cp", 0))
        super().hitattr_make(name, base, group, aseq, attr, onhit=onhit, dtype=dtype)

    def update_radiance(self, delta):
        self.radiance_gauge = max(min(self.radiance_gauge + delta, 100), 0)

    def reset_radiance(self, e):
        self.radiance_gauge = 0

    @property
    def radiance_level(self):
        return self.radiance_gauge // 33

    def a1_get(self):
        return (0.0, 0.3, 0.5, 0.0)[self.radiance_level]

    def s1_before(self, e):
        if 68 <= self.radiance_gauge < 100:
            self.radiance = Modifier("ravishing_radiance", "s", "passive", 1.0).on()

    def s1_proc(self, e):
        if self.radiance_gauge == 100:
            self.radiance.off()

    def s2_proc(self, e):
        self.dragonform.charge_gauge(100, dhaste=False)


variants = {None: Summer_Chelle}
