from core.advbase import *
from slot.a import *
from slot.d import *

def module():
    return Yaten

class Yaten(Adv):
    a1 = [('estat_att', 3), ('estat_crit', 3)]
    a3 = ('energized_att', 0.20)
    conf = {}
    conf['slots.a'] = The_Shining_Overlord()+The_Fires_of_Hate()
    conf['acl'] = """
        `dragon(c3-s-end), fsc and self.energy() = 5
        `s3, not self.s3_buff
        `s4
        `s1
        `s2, fsc and self.energy() < 4
        `fs, x=3
    """
    conf['coabs'] = ['Ieyasu','Wand','Delphi']
    conf['share'] = ['Kleimann']

    def d_skillshare(self):
        if self.sim_afflict:
            self.conf['share'] = ['Curran']

    def d_coabs(self):
        if self.sim_afflict:
            self.conf['coabs'] = ['Ieyasu','Wand','Bow']

    def s1_proc(self, e):
        if self.energy() == 5:
            self.dmg_make(f'o_{e.name}_boost',6*0.69)
        self.energy.add(1)

    def s2_proc(self, e):
        self.energy.add(2, team=True)


if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
