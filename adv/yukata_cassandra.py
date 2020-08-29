import adv.adv_test
from core.advbase import *
from slot.a import *
from slot.d import *

def module():
    return Yukata_Cassandra

echo_mod = 0.20

class Yukata_Cassandra(Adv):
    comment = 's1 team buff not considered'
    a1 = ('a',0.20,'hp100')

    conf = {}
    conf['slots.a'] = Proper_Maintenance()+The_Bridal_Dragon()
    conf['acl'] = """
        `dragon
        `s3, not self.s3_buff
        `s4
        `s1
    """
    coab = ['Marth', 'Blade', 'Tobias']
    share = ['Emma']

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