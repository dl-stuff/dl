import adv.adv_test
from core.advbase import *
from slot.a import *
from slot.d import *
def module():
    return Marty

class Marty(Adv):
    a1 = ('sp',0.05)
    conf = {}
    conf['slots.a'] = TSO()+The_Lurker_in_the_Woods()
    conf['slot.d'] = Dreadking_Rathalos()
    conf['acl'] = """
        `dragon, fsc
        `s3, fsc and not this.s3_buff_on
        `s1, fsc
        `fs, seq=2
        """



if __name__ == '__main__':
    conf = {}
    adv.adv_test.test(module(), conf)

