from core.advbase import *


class Humanoid_Mercury(Adv):
    def prerun(self):
        Event("dragon").listener(self.a1_on, order=0)
        self.a3_regen = Timer(self.a3_regen, 2.9, True).on()
        self.bubble_shield = EffectBuff("bubble_shield", -1, dummy_function, dummy_function)

    @staticmethod
    def prerun_skillshare(adv, dst):
        adv.current_s[dst] = "teamamp"

    def a1_on(self, e):
        if self.dragonform.shift_count == 2:
            self.dragonform.conf.update(self.conf.dragonform2)

    @allow_acl
    def s(self, n):
        if self.amp_lvl(kind="team", key=2) >= 1:
            self.current_s["s1"] = "teamamp"
        return super().s(n)

    def a3_regen(self, t):
        # theres a 10s cd that im choosing to ignore
        if self.amp_lvl(kind="team", key=2) >= 1:
            self.bubble_shield.on()
            self.add_hp(5)
        else:
            self.bubble_shield.off()


variants = {None: Humanoid_Mercury}
