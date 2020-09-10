from core.advbase import *
from slot.a import *
from slot.d import *


def module():
    return Forte


class Forte(Adv):
    a3 = ('k_poison', 0.30)

    conf = {}
    conf['slots.a'] = Dragon_and_Tamer()+The_Red_Impulse()
    conf['slots.d'] = Ramiel()
    conf['slots.poison.d'] = Gala_Cat_Sith()
    conf['acl'] = """
        if self.sim_afflict
        `dragon(c3-s-end), x=5
        `s3, not buff(s3)
        `s2
        `s4, cancel or s=2
        `s1
        `fs, x=5
        else
        `dragon(c3-s-end), s2.charged<s2.sp/3 and cancel
        `s3, not buff(s3)
        `s2
        `s4
        `s1, cancel or self.afflics.poison.get()
        `fs, x=5
        end
        """
    conf['coabs'] = ['Ieyasu', 'Wand', 'Cleo']
    conf['share'] = ['Kleimann']

    def d_coabs(self):
        if self.sim_afflict:
            self.conf['share'] = ['Curran']

    def prerun(self):
        self.dgauge_charge = 40

    @staticmethod
    def prerun_skillshare(adv, dst):
        adv.dgauge_charge = 0

    def s1_proc(self, e):
        self.dragonform.charge_gauge(self.dgauge_charge, dhaste=False)
        with KillerModifier('s1_killer', 'hit', 0.3, ['poison']):
            self.dmg_make(e.name, 11.34)

    def s2_proc(self, e):
        self.dragonform.charge_gauge(self.dgauge_charge, dhaste=False)
        Selfbuff(e.name, 0.20, 15, 'att', 'buff')


if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
