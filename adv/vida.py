import adv.adv_test
from core.advbase import *
from slot.a import *
from slot.d import *

def module():
    return Vida

class Vida(Adv):
#    comment = 'unsuitable resist'
    a1 = ('fs',0.30)
    conf = {}
    conf['slot.a'] = Twinfold_Bonds()+The_Lurker_in_the_Woods()
    conf['slot.d'] = Fatalis()
    conf['acl'] = """
        `s3, not this.s3_buff
        `s1
        `s2
        `fs, x=2
        """

    def prerun(self):
        self.s2charge = 0

    def s2_proc(self, e):
        self.s2charge = 3

    def fs_proc(self, e):
        if self.s2charge > 0:
            self.s2charge -= 1
            self.dmg_make("o_fs_boost",0.21*3)



if __name__ == '__main__':
    conf = {}
    adv.adv_test.test(module(), conf)

