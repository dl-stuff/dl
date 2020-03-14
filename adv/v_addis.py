from core.advbase import *
from slot.d import *
from slot.a import *

def module():
    return Valentines_Addis

class Valentines_Addis(Adv):
    comment = 'use s2 once'

    a1 = ('k_poison',0.3)
    conf = {}
    conf['slot.d'] = Shinobi()
    conf['slot.a'] = The_Plaguebringer()+Primal_Crisis()
    conf['acl'] = """
        `s3, not self.s3_buff
        `s2, self.hp > 30
        `s1
    """
    conf['afflict_res.poison'] = 0

    def prerun(self):
        self.hp = 100
        self.a3atk = Selfbuff('a3atk',0.20,-1,'att','passive')
        self.a3spd = Spdbuff('a3spd',0.10,-1)

    def s1_proc(self, e):
        with CrisisModifier('s1', 1.25, self.hp):
            self.afflics.poison('s1', 120, 0.582)
            self.dmg_make('s1', 8.60)

    def s2_proc(self, e):
        if self.hp > 30:
            self.hp = 20
            self.a3atk.on()
            self.a3spd.on()

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
