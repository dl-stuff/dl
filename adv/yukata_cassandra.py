from core.advbase import *
from slot.a import *
from slot.d import *

def module():
    return Yukata_Cassandra

echo_mod = 0.20

class Yukata_Cassandra(Adv):
    comment = 's1 team buff not considered'

    conf = {}
    conf['slots.a'] = Proper_Maintenance()+Jewels_of_the_Sun()
    conf['slots.burn.a'] = conf['slots.a']
    conf['acl'] = """
        `dragon, s
        `s3, not buff(s3) and x=5
        `s4
        `s1, x>3
    """
    conf['coabs'] = ['Marth', 'Blade', 'Tobias']
    conf['share'] = ['Karl']

    @staticmethod
    def setup_fluorescent_fish(adv):
        # actually a teambuff
        adv.fluorescent_fish = EffectBuff(
            'fluorescent_fish', 15,
            lambda: adv.enable_echo(mod=echo_mod),
            lambda: adv.disable_echo()
        )

    def prerun(self):
        Yukata_Cassandra.setup_fluorescent_fish(self)
        self.a3_att_mod = Modifier('a3_att', 'att', 'passive', 0.30, get=self.a3_get)

    @staticmethod
    def prerun_skillshare(adv, dst):
        Yukata_Cassandra.setup_fluorescent_fish(adv)

    def a3_get(self):
        return self.s2.sp==self.s2.charged

    def s1_proc(self, e):
        self.fluorescent_fish.on()

if __name__ == '__main__':
    import sys
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)