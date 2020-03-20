import adv.adv_test
from core.advbase import *
from slot.a import *
from slot.d import *

def module():
    return Yuya

class Yuya(Adv):
    comment = 'c2fs; no s2'
    
    conf = {}
    conf['slot.a'] = TB() + The_Lurker_in_the_Woods()
    conf['slot.d'] = Dreadking_Rathalos()
    conf['acl'] = """
        `s3, fsc and not self.s3_buff
        `s1, fsc
        `fs, x = 2
        """

    a3 = ('primed_crit_chance', 0.5,5)

    def prerun(self):
        if self.condition('hp60'):
            Selfbuff('a1',0.2,-1,'att','passive').on()
        else:
            Selfbuff('a1',-0.2,-1,'att','passive').on()

    def s1_proc(self, e):
        Spdbuff("s2",0.2, 10)

if __name__ == '__main__':
    conf = {}
    adv.adv_test.test(module(), conf)

