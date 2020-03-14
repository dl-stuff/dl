import adv.adv_test
from core.advbase import *
from core.log import *
from slot.a import *
from slot.d import *

def module():
    return Valentines_Orion

class Valentines_Orion(Adv):
    conf = {}

    conf['acl'] = """
        ``dragon, fsc
        `s3, fsc and not this.s3_buff_on
        `s1, fsc
        `fs, seq=3 and cancel
        """
    conf['slot.a'] = TSO()+EE()
    conf['slot.d'] = Apollo()
    conf['afflict_res.burn'] = 0

    def prerun(self):
        self.dc_event = Event('defchain')

    def s1_proc(self, e):
        self.afflics.burn('s1',100,0.803)


    def s2_proc(self, e):
        self.dc_event()


if __name__ == '__main__':
    conf = {}
    adv.adv_test.test(module(), conf)

