from core.advbase import *
from slot.a import *

def module():
    return Cassandra

class Cassandra(Adv):
    a1 = ('prep_charge',0.05)
    a3 = ('ro', 0.15)

    conf = {}
    conf['slots.a'] = Candy_Couriers()+The_Plaguebringer()
    conf['acl'] = """
        `dragon.act('c3 s end')
        `s3, not this.s3_buff
        `s1
        `s2, x=5
    """
    conf['afflict_res.poison'] = 0

    def prerun(self):
        self.hp = 80

    def s1_proc(self, e):
        self.afflics.poison('s1',120,0.582)

    def s2_proc(self, e):
        with CrisisModifier('s2', 1, self.hp):
            self.dmg_make('s2',9.72)

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
