from core.advbase import *
from slot.a import *

def module():
    return Valentines_Addis

class Valentines_Addis(Adv):
    comment = 'use s2 once'

    a1 = ('k_poison',0.3)
    a3 = ('crisisattspd', 3)
    
    conf = {}
    conf['slots.a'] = Forest_Bonds()+Primal_Crisis()
    conf['slots.poison.a'] = conf['slots.a']
    conf['acl'] = """
        `dragon(c3-s-end), (self.hp>0 and (self.trickery <= 0 or self.sim_afflict)) or (self.hp=0 and x=5)
        `s3, not self.s3_buff
        `s2, self.hp > 30
        `s1
        `s4
        `fs, x=5
    """
    conf['coabs'] = ['Wand','Curran','Summer_Patia']
    conf['afflict_res.poison'] = 0
    conf['share'] = ['Veronica']

    def s1_proc(self, e):
        with CrisisModifier(e.name, 1.25, self.hp):
            self.afflics.poison(e.name, 120, 0.582)
            self.dmg_make(e.name, 8.60)

    def s2_proc(self, e):
        if self.hp > 30:
            self.set_hp(20)

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
