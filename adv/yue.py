import adv.adv_test
from core.advbase import *
from slot.a import *
from slot.d import *

def module():
    return Yue

class Yue(Adv):
    conf = {}
    conf['slot.a'] = Kung_Fu_Masters()+Flower_in_the_Fray()
    conf['slot.d'] = Arctos()
    conf['acl'] = """
        `dragon, s=2
        `s3, not this.s3_buff
        `s1
        `s2, fsc
        `fs, x=5
        """



if __name__ == '__main__':
    conf = {}
    adv.adv_test.test(module(), conf)

