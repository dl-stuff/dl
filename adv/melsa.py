import adv.adv_test
from core.advbase import *
from slot.a import *
from slot.d import *

def module():
    return Melsa

class Melsa(Adv):
    comment = "c2fs"
    
    a3 = ('cc',0.08,'hit15')
    conf = {}
    conf['slot.a'] = TB() + The_Lurker_in_the_Woods()
    conf['slot.d'] = Dreadking_Rathalos()
    conf['acl'] = """
        `s3, not self.s3_buff
        `s1, fsc
        `s2, fsc
        `fs, x=2
    """

if __name__ == '__main__':
    conf = {}
    adv.adv_test.test(module(), conf)

