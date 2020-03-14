import adv.adv_test
from core.advbase import *
from slot.a import *
from slot.d import *

def module():
    return Alain

class Alain(Adv):
    conf = {}
    conf['slot.a'] = RR()+EE()
    conf['slot.d'] = Apollo()
    conf['acl'] = """
        `dragon, x=5
        `s3, not this.s3_buff_on
        `s1
        `s2
        `fs, x=5
        """
    conf['afflict_res.burn'] = 0

    def s1_proc(self, e):
        self.afflics.burn('s1',100,0.803)
    
    def s2_proc(self, e):
        self.afflics.burn('s2',100,0.803)

if __name__ == '__main__':
    conf = {}
    adv.adv_test.test(module(), conf)

