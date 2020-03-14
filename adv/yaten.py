from core.advbase import *
from slot.a import *

def module():
    return Yaten

class Yaten(Adv):
    a1 = ('epassive_att_crit', 3)
    a3 = ('energized_att', 0.20)
    
    conf = {}
    conf['slot.a'] = The_Shining_Overlord()+JotS()
    conf['acl'] = """
        `dragon
        `s3, not this.s3_buff
        `s1
        `s2, fsc and this.energy() < 4
        `fs, seq=3
    """

    def d_slots(self):
        if 'bow' in self.ex:
            self.conf.slot.a = TSO()+BN()

    def s1_proc(self, e):
        if self.energy() == 5:
            self.dmg_make('o_s1_boost',6*0.69)
        self.energy.add(1)

    def s2_proc(self, e):
        self.energy.add(2, team=True)

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
