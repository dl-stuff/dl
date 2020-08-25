from core.advbase import *
from slot.a import *

def module():
    return Naveed

class Naveed(Adv):
    a1 = ('a',0.08,'hit15')
    a3 = ('prep','100%')
    conf = {}
    conf['acl'] = """
        `dragon.act('c1 s s end'),s
        `s3, not self.s3_buff
        `s2, self.s1level < 5
        `s1, cancel
        `s4, fsc
        `fs, x=3 and cancel
        """
    conf['slots.a'] = The_Shining_Overlord()+Primal_Crisis()
    coab = ['Blade', 'Wand', 'Marth']
    share = ['Summer_Patia']

    def prerun(self):
        self.s1level = 0

    @staticmethod
    def prerun_skillshare(adv, dst):
        adv.s1level = 0

    def s1_proc(self, e):
        for _ in range(self.s1level):
            for _ in range(3):
                self.dmg_make(e.name,0.7)
                self.add_hits(1)

    def s2_proc(self, e):
        self.s1level += 1
        if self.s1level >= 5:
            self.s1level = 5
        Selfbuff(e.name+'_defense', 0.20, 10, 'defense').on()

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
