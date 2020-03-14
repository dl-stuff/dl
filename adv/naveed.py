import adv.adv_test
from core.advbase import *
from core.advbase import *
from slot.a import *

def module():
    return Naveed

class Naveed(Adv):
    a1 = ('a',0.08,'hit15')
    a3 = ('prep','100%')
    conf = {}
    conf['acl'] = """
        `dragon.act('c3 s end')
        `s3, not this.s3_buff_on
        `s2, this.s1level < 5
        `s1
        `fs, x=3
        """
    conf['slot.a'] = TSO()+Primal_Crisis()
            
    def prerun(self):
        self.s1level = 0

    def s1_proc(self, e):
        for _ in range(self.s1level):
            for _ in range(3):
                self.dmg_make("o_s1_boost",0.7,'s')
                self.hits += 1

    def s2_proc(self, e):
        self.s1level += 1
        if self.s1level >= 5:
            self.s1level = 5
        adv.Event('defchain')()

if __name__ == '__main__':
    conf = {}
    adv.adv_test.test(module(), conf)

