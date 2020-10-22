from core.advbase import *

echo_mod = 0.40
class Yukata_Cassandra(Adv):
    comment = 's1 team buff not considered'

    @staticmethod
    def config_fluorescent_fish(adv):
        # actually a teambuff
        adv.fluorescent_fish = EffectBuff(
            'fluorescent_fish', 15,
            lambda: adv.enable_echo(mod=echo_mod),
            lambda: adv.disable_echo()
        )

    def prerun(self):
        Yukata_Cassandra.config_fluorescent_fish(self)
        self.a3_att_mod = Modifier('a3_att', 'att', 'passive', 0.30, get=self.a3_get)

    @staticmethod
    def prerun_skillshare(adv, dst):
        Yukata_Cassandra.config_fluorescent_fish(adv)

    def a3_get(self):
        return self.s2.sp == self.s2.charged

    def s1_proc(self, e):
        self.fluorescent_fish.on()

variants = {None: Yukata_Cassandra}
