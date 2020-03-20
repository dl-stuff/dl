import adv.adv_test
from core.advbase import *
from slot.a import *
from slot.d import *

def module():
    return Joe

class Joe(Adv):
    comment = 'c1fs'
    
    conf = {}
    conf['slot.a'] = MF() + DD()
    conf['slot.d'] = Dreadking_Rathalos()
    conf['acl'] = """
        `s3, fsc and not self.s3_buff
        `s1, fsc
        `s2, fsc
        `fs, x = 1
        """
    conf['afflict_res.burn'] = 0

    def prerun(self):
        if self.condition('hp100'):
            self.fullhp = 1
        else:
            self.fullhp = 0

    def s1_proc(self, e):
        self.afflics.burn('s1',100+70*self.fullhp,0.803)
        
    def s2_proc(self, e):
        self.afflics.burn('s2',100+70*self.fullhp,0.803)

if __name__ == '__main__':
    conf = {}
    adv.adv_test.test(module(), conf)

