import adv.adv_test
from core.advbase import *
from slot.a import *
from slot.d import *

def module():
    return Marty

class Marty(Adv):
    comment = 'c2fs'
    a1 = ('sp',0.05)
    
    conf = {}
    conf['slot.a'] = RR() + The_Lurker_in_the_Woods()
    conf['slot.d'] = Dreadking_Rathalos()
    conf['acl'] = """
        `s3, fsc and not self.s3_buff
        `s1, fsc
        `fs, x = 2
        """



if __name__ == '__main__':
    conf = {}
    adv.adv_test.test(module(), conf)

