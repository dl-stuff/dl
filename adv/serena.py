import adv.adv_test
from core.advbase import *
from slot.a import *
from slot.d import *

def module():
    return Serena

class Serena(Adv):
    comment = 'c2fs'
    
    conf = {}
    conf['slot.a'] = MF() + PC()
    conf['slot.d'] = Dreadking_Rathalos()
    conf['acl'] = """
        `s3, fsc and not self.s3_buff
        `s1, fsc
        `s2, fsc
        `fs, x = 2
        """

    def s1_before(self, e):
        Selfbuff('s1buff',0.1,5,'crit','rate').on()


    def init(self):
        if self.condition('always connect hits'):
            self.dmg_proc = self.c_dmg_proc


    def prerun(self):
        self.hits = 0
        self.a1count = 0
        self.a3count = 0


    def c_dmg_proc(self, name, amount):
        a1old = self.a1count
        if self.hits > 60:
            self.a1count = 3
        elif self.hits > 40:
            self.a1count = 2
        elif self.hits > 20:
            self.a1count = 1
        if a1old != self.a1count:
            Selfbuff('a1buff',0.06,-1,'crit','damage').on()

        a3old = self.a3count
        if self.hits > 90:
            self.a3count = 3
        elif self.hits > 60:
            self.a3count = 2
        elif self.hits > 30:
            self.a3count = 1
        if a3old != self.a3count:
            Selfbuff('a3buff',0.03,-1,'crit','chance').on()




if __name__ == '__main__':
    conf = {}
    adv.adv_test.test(module(), conf)

