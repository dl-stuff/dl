import adv.adv_test
from core.advbase import *
from slot.a import *
from slot.d import *

def module():
    return Xania

class Xania(Adv):
    comment = ''
    a1 = ('s',0.35)
    
    conf = {}
    conf['slot.a'] = CC() + PC()
    conf['slot.d'] = Apollo()
    conf['acl'] = """
        `s3, not self.s3_buff
        `s1
        `s2
        """
    conf['afflict_res.burn'] = 0

    def s1_proc(self, e):
        self.afflics.burn('s1',100,0.803)

    def s2_proc(self, e):
        self.afflics.burn('s2',100,0.803)

if __name__ == '__main__':
    conf = {}
    adv.adv_test.test(module(), conf)
