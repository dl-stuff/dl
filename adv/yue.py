import adv.adv_test
from core.advbase import *
from slot.a import *
from slot.d import *

def module():
    return Yue

class Yue(Adv):
    comment = "c5fs"
        
    conf = {}
    conf['slot.a'] = KFM() + TWD()
    conf['slot.d'] = Arctos()
    conf['acl'] = """
        `s3, not self.s3_buff
        `s1, cancel
        `s2, fsc
        `fs, x=5
        """



if __name__ == '__main__':
    conf = {}
    adv.adv_test.test(module(), conf)

