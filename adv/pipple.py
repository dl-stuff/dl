from core.advbase import *
from slot.a import *
from slot.d import *

def module():
    return Pipple

pipple_conf = {
    'x1.dmg': 2.21,
    'x2.dmg': 1.19*2,
    'x3.dmg': 0.80*3,
    'x4.dmg': 1.65*2,
    'x5.dmg': 0.80*4+1.32,
}

class Pipple(Adv):
    a3 = [('estat_att', 7), ('estat_crit', 7)]

    conf = pipple_conf.copy()
    conf['slots.a'] = Proper_Maintenance()+Brothers_in_Arms()
    conf['slots.frostbite.a'] = conf['slots.a']
    conf['slots.d'] = Gaibhne_and_Creidhne()
    conf['acl'] = """
        `dragon(c3-s-end),x=5
        `s2, (x=5 or s) and not self.energy()=5
        `s4
        `s3, cancel
        `s1, x>2
        """
    conf['coabs'] = ['Tiki', 'Renee', 'Tobias']
    conf['share'] = ['Summer_Luca','Patia']

    def prerun(self):
        self.phase['s1'] = 0

    @staticmethod
    def prerun_skillshare(self, dst):
        self.phase[dst] = 0

    def s1_proc(self, e):
        Teambuff(e.name, 0.25, 15, 'defense').on()
        self.phase[e.name] += 1
        if self.phase[e.name] == 2:
            self.energy.add(1)
        self.phase[e.name] %= 3

    def s2_proc(self, e):
        self.energy.add(2, team=True)

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)