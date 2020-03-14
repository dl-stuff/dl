import adv.adv_test
from core.advbase import *

def module():
    return Berserker

class Berserker(Adv):
    a3 = ('lo',0.3)
    conf = {}
    conf['acl'] = """
        `dragon, x=5
        `s3, not this.s3_buff
        `s1
        `s2
        `fs, x=5
        """

if __name__ == '__main__':
    conf = {}
    adv.adv_test.test(module(), conf)

